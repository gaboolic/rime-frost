local log = require("trans_log")
local http = require("simplehttp")
-- 全局 HTTP 超时（秒），避免网络不通时卡住引擎线程
http.TIMEOUT = 5
local json = require("trans_json")
local sha = require("trans_sha2")

-- 翻译API配置
local config = {
    -- 选择使用的翻译API: "google", "deepl", "microsoft", "deeplx", "niutrans", "youdao", "baidu"
    -- 百度翻译暂时不可用，请勿使用
    default_api = "google",

    -- API密钥配置
    api_keys = {
        deepl = "YOUR_DEEPL_API_KEY", -- DeepL API密钥
        microsoft = {
            key = "YOUR_MS_TRANSLATOR_API_KEY", -- Microsoft Translator API密钥
            region = "global" -- 替换为您的区域
        },
        niutrans = "YOUR_NIUTRANS_API_KEY", -- 小牛云翻译API密钥
        youdao = {
            app_id = "YOUR_YOUDAO_APP_ID", -- 有道翻译应用ID
            app_key = "YOUR_YOUDAO_APP_KEY" -- 有道翻译应用密钥
        },
        baidu = {
            app_id = "YOUR_BAIDU_APP_ID", -- 百度翻译应用ID
            app_key = "YOUR_BAIDU_APP_KEY" -- 百度翻译应用密钥
        }
    }
}

-- URL编码函数
local function url_encode(str)
    if str then
        str = string.gsub(str, "\n", "\r\n")
        str = string.gsub(str, "([^%w %-%_%.%~])",
            function(c)
                return string.format("%%%02X", string.byte(c))
            end)
        str = string.gsub(str, " ", "+")
    end
    return str
end

-- Google翻译API
local function google(text)
    local encoded_text = url_encode(text)
    local url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=en&dt=t&dt=bd&dt=rm&dt=qca&dt=at&dt=ss&dt=md&dt=ld&dt=ex&dj=1&q=" .. encoded_text

    log.info("google start: " .. url)
    local t0 = os.time()
    local reply = http.request(url)
    local dt = os.difftime(os.time(), t0)
    local rlen = reply and #reply or -1
    log.info(string.format("google done: len=%d dt=%ds", rlen, dt))
    local success, j = pcall(json.decode, reply)

    if success and j then
        if j.dict and j.dict[1] and j.dict[1].terms and j.dict[1].terms[1] then
            return j.dict[1].terms[1]
        end
        if j.sentences and j.sentences[1] and j.sentences[1].trans then
            return j.sentences[1].trans
        end
    end

    if reply then
        local _, _, terms = string.find(reply, '"terms":%[%"([^"]+)"')
        if terms then
            return terms
        end

        local _, _, translated = string.find(reply, '"trans":"([^"]+)"')
        if translated then
            return translated
        end

        local _, _, translated2 = string.find(reply, '%[%[%["([^"]+)"')
        if translated2 then
            return translated2
        end
    end

    return nil
end

-- DeepL翻译API
local function deepl(text)
    local api_key = config.api_keys.deepl
    if not api_key then
        return nil
    end

    local url = "https://api-free.deepl.com/v2/translate"
    local body = "auth_key=" .. api_key .. "&text=" .. url_encode(text) .. "&target_lang=EN"

    local headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded"
    }

    local reply = http.request{
        url = url,
        method = "POST",
        headers = headers,
        data = body
    }
    local success, j = pcall(json.decode, reply)

    if success and j and j.translations and j.translations[1] and j.translations[1].text then
        return j.translations[1].text
    end

    return nil
end

-- Microsoft翻译API
local function microsoft(text)
    local api_key = config.api_keys.microsoft.key
    local region = config.api_keys.microsoft.region

    if not api_key then
        return nil
    end

    local url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=en"
    local body = json.encode({
        {["Text"] = text}
    })

    local headers = {
        ["Content-Type"] = "application/json",
        ["Ocp-Apim-Subscription-Key"] = api_key,
        ["Ocp-Apim-Subscription-Region"] = region
    }

    local reply = http.request{
        url = url,
        method = "POST",
        headers = headers,
        data = body
    }
    local success, j = pcall(json.decode, reply)

    if success and j and j[1] and j[1].translations and j[1].translations[1] and j[1].translations[1].text then
        return j[1].translations[1].text
    end

    return nil
end

-- 小牛云翻译API
local function niutrans(text)
    local api_key = config.api_keys.niutrans
    if not api_key then
        return nil
    end

    local url = "https://api.niutrans.com/NiuTransServer/translation"

    local body = json.encode({
        from = "zh",
        to = "en",
        apikey = api_key,
        src_text = text
    })

    local headers = {
        ["Content-Type"] = "application/json"
    }

    local reply = http.request{
        url = url,
        method = "POST",
        headers = headers,
        data = body
    }

    if not reply or reply == "" then
        return nil
    end

    local success, j = pcall(json.decode, reply)
    if not success then
        return nil
    end

    if j.tgt_text then
        if type(j.tgt_text) == "string" then
            local inner_success, inner_json = pcall(json.decode, j.tgt_text)
            if inner_success and type(inner_json) == "table" then
                return inner_json.content
            else
                return j.tgt_text
            end
        elseif type(j.tgt_text) == "table" then
            if j.tgt_text.content then
                return j.tgt_text.content
            else
                for k, v in pairs(j.tgt_text) do
                    if type(v) == "string" then
                        return v
                    end
                end
                return nil
            end
        else
            return nil
        end
    elseif j.translation then
        return j.translation
    elseif j.result and j.result.translatedText then
        return j.result.translatedText
    else
        return nil
    end
end

-- 有道翻译API
local function youdao(text)
    local app_id = config.api_keys.youdao.app_id
    local app_key = config.api_keys.youdao.app_key

    if not app_id or not app_key then
        log.error("有道API密钥未配置")
        return nil
    end

    local salt = tostring(math.random(32768, 65536))
    local curtime = tostring(os.time())
    local function get_input(q)
        if #q <= 20 then return q end
        return q:sub(1,10) .. tostring(#q) .. q:sub(-10)
    end
    local input = get_input(text)
    local sign_str = app_id .. input .. salt .. curtime .. app_key
    local sign = sha.sha256(sign_str)

    local url = "https://openapi.youdao.com/api"
    local body = "q=" .. url_encode(text)
        .. "&from=zh-CHS&to=en"
        .. "&appKey=" .. app_id
        .. "&salt=" .. salt
        .. "&sign=" .. sign
        .. "&signType=v3"
        .. "&curtime=" .. curtime

    local headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded"
    }

    log.info("有道翻译请求URL: " .. url)
    log.info("有道翻译请求体: " .. body)

    local reply = http.request{
        url = url,
        method = "POST",
        headers = headers,
        data = body
    }

    if not reply or reply == "" then
        log.error("有道翻译收到空响应")
        return nil
    end

    log.info("有道翻译响应: " .. reply)

    local success, j = pcall(json.decode, reply)
    if not success then
        log.error("有道翻译JSON解析失败: " .. tostring(j))
        return nil
    end

    if j and j.translation and j.translation[1] then
        log.info("有道翻译结果: " .. tostring(j.translation[1]))
        return j.translation[1]
    elseif j and j.basic and j.basic.explains and j.basic.explains[1] then
        log.info("有道翻译basic.explains: " .. tostring(j.basic.explains[1]))
        return j.basic.explains[1]
    else
        log.error("有道翻译未找到有效结果")
        return nil
    end
end

-- 百度翻译API
local function baidu(text)
    local app_id = config.api_keys.baidu.app_id
    local app_key = config.api_keys.baidu.app_key

    if not app_id or not app_key then
        log.error("百度API密钥未配置")
        return nil
    end

    local salt = tostring(math.random(32768, 65536))
    local sign = sha.md5(app_id .. text .. salt .. app_key):lower()

    local url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    local body = "q=" .. url_encode(text)
        .. "&from=zh&to=en"
        .. "&appid=" .. app_id
        .. "&salt=" .. salt
        .. "&sign=" .. sign

    local headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded"
    }

    log.info("百度翻译请求URL: " .. url)
    log.info("百度翻译请求体: " .. body)

    local reply = http.request{
        url = url,
        method = "POST",
        headers = headers,
        data = body
    }

    if not reply or reply == "" then
        log.error("百度翻译收到空响应")
        return nil
    end

    log.info("百度翻译响应: " .. reply)

    local success, j = pcall(json.decode, reply)
    if not success then
        log.error("百度翻译JSON解析失败: " .. tostring(j))
        return nil
    end

    if j and j.trans_result and j.trans_result[1] and j.trans_result[1].dst then
        log.info("百度翻译结果: " .. tostring(j.trans_result[1].dst))
        return j.trans_result[1].dst
    else
        log.error("百度翻译未找到有效结果")
        return nil
    end
end

-- 导出模块
return {
    google = google,
    deepl = deepl,
    microsoft = microsoft,
    niutrans = niutrans,
    youdao = youdao,
    baidu = baidu,
    config = config
}
