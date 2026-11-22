-- 白霜句中任意辅助码候选筛选滤镜。
--
-- 用法：
--   在方案的 filters 中加入本滤镜，建议放在主要候选已经生成之后、
--   simplifier / uniquifier 之前：
--
--     - lua_filter@*aux_lookup_filter
--
--   可选配置：
--
--     frost_aux_filter:
--       trigger_key: "`"
--
-- 大致流程：
--   1. 普通输入没有触发键时，直接原样透传候选。
--   2. 输入包含触发键时，例如 `shishi`b`，读取触发键后的辅码，
--      并用 `lua/aux_code/moqi_aux_code.txt` 中的墨奇辅助码筛选现有候选。
--   3. 单字查字主要由 `table_translator@frost_aux` 处理；本滤镜主要负责
--      词组和整句候选筛选。
--   4. 选中候选后，自动从 `ctx.input` 中移除触发键和辅码，并提交当前候选，
--      避免辅码残留，也避免需要按两次空格。
--
-- 基础例子：
--   shishi`b  -> 事实 / 实施 / 实时 ...  因为 实=bd
--   shishi`y  -> 试试 / 史诗 ...         因为 试=yg, 诗=ys
--   ni`rx     -> 你 / 伱                 因为 你=rx
--
-- 整句筛选：
--   当同长度候选只在少数位置不同，本滤镜会优先只检查这些“差异位置”的辅码，
--   而不是匹配整句里任意一个无关的字。这样可以处理整句候选的局部纠错。
--
--   例子 1：
--
--     我非常嫉妒
--     我非常极度
--
--   按 `m 可以把“我非常极度”作为首选，因为 极=mj。
--
--   例子 2：
--
--     像个傻子使得
--     像个傻子似的
--     像个傻子时的
--
--   按 `r 可以让“像个傻子似的”作为首选，因为 似=rr。
--   按 `o 可以让“像个傻子时的”作为首选，因为 时=oc。
--
--   例子 3：
--
--     忍不住地流行
--     忍不住的流行
--     忍不住的流星
--
--   按 `o 可以让“忍不住的流星”到最前，因为 星=ou。
--
--   另一个例子：
--
--     极度你的爱气势如虹
--     嫉妒你的爱气势如虹
--     季度你的爱气势如虹
--
--   输入 `...`n` 会优先选择“嫉妒...”开头的候选，因为 嫉=nu / 妒=nh，
--   而 极=mj、季=hz 不匹配 `n`。

local M = {}

-- 空串表示未启用，"!" 表示逐字模式正等待辅码。辅码不写进 ctx.input，
-- 因此原生部分候选可以只消耗自己的音节，Rime 也能按纯音码学习整词。
local char_aux_property = "frost_char_aux"
local waiting = "!"
local char_processor = {}
M.char_processor = char_processor

function char_processor.init(env)
    local config = env.engine.schema.config
    local trigger = config:get_string("frost_aux_filter/char_trigger") or "``"
    -- 双键引导的第一键必须是可进入组字缓冲的标点，如默认的反引号。
    if #trigger == 2 and trigger:match("^%p%p$") then
        env.lead, env.tail = trigger:sub(1, 1), trigger:byte(2)
    end
    local ctx = env.engine.context
    env.char_select = ctx.select_notifier:connect(function(context)
        local aux = context:get_property(char_aux_property)
        if aux ~= "" and aux ~= waiting then
            context:set_property(char_aux_property, waiting)
        end
    end, 0) -- 在引擎生成下一段候选前，清掉已选单字的辅码。
    local function reset(context)
        if context:get_property(char_aux_property) ~= "" then
            context:set_property(char_aux_property, "")
        end
    end
    env.char_commit = ctx.commit_notifier:connect(reset)
    env.char_update = ctx.update_notifier:connect(function(context)
        if context.input == "" then reset(context) end
    end)
end

function char_processor.func(key, env)
    -- 允许 Shift 打出标点；逐字辅码本身也统一按小写处理。
    if not env.tail or (key.modifier ~= 0 and key.modifier ~= 1) then return 2 end
    local ctx = env.engine.context
    local code = key.keycode
    local aux = ctx:get_property(char_aux_property)
    if aux == "" then
        if code == env.tail and not ctx:get_option("ascii_mode") and ctx.caret_pos == #ctx.input
            and ctx.input:sub(-1) == env.lead and ctx.input:sub(1, -2):match("^[a-zA-Z';]+$") then
            ctx:set_property(char_aux_property, waiting)
            ctx:pop_input(1)
            return 1
        end
        return 2
    end
    if ctx:get_option("ascii_mode") or code == 0xff1b then -- Escape 交还给 Rime。
        ctx:set_property(char_aux_property, "")
        ctx:refresh_non_confirmed_composition()
        return 2
    end
    if code == 0xff08 then -- BackSpace：先删辅码，再退出逐字模式。
        local remaining = aux == waiting and "" or (#aux == 1 and waiting or aux:sub(1, -2))
        ctx:set_property(char_aux_property, remaining)
        ctx:refresh_non_confirmed_composition()
        return 1
    end
    if (code >= 97 and code <= 122) or (code >= 65 and code <= 90) then
        if aux == waiting then aux = "" end
        if #aux < 2 then
            ctx:set_property(char_aux_property, aux .. string.char(code):lower())
            ctx:refresh_non_confirmed_composition()
        end
        return 1
    end
    return 2
end

function char_processor.fini(env)
    env.char_select:disconnect()
    env.char_commit:disconnect()
    env.char_update:disconnect()
end

local function escape_pattern(s)
    return (s:gsub("(%W)", "%%%1"))
end

local function pass_through(input)
    for cand in input:iter() do
        yield(cand)
    end
end

-- 延迟加载墨奇辅助码表。
--
-- 文件格式：
--   字=aux
-- 示例：
--   你=rx
--   嫉=nu
--
-- 读取结果会缓存在模块表上；普通输入没有触发键时不会加载码表。
local function load_aux_table()
    if M.aux_table then
        return M.aux_table
    end

    local aux_table = {}
    local file = io.open(rime_api.get_user_data_dir() .. "/lua/aux_code/moqi_aux_code.txt", "r")
    if not file and rime_api.get_shared_data_dir then
        file = io.open(rime_api.get_shared_data_dir() .. "/lua/aux_code/moqi_aux_code.txt", "r")
    end
    if not file then
        M.aux_table = aux_table
        return aux_table
    end

    for line in file:lines() do
        local ch, code = line:match("^([^=]+)=(.+)$")
        if ch and code and code ~= "" then
            local codes = aux_table[ch]
            -- 大多数汉字只有一码，不为每个字分配一个单元素表。
            if not codes then
                aux_table[ch] = code
            elseif type(codes) == "string" then
                aux_table[ch] = { codes, code }
            else
                codes[#codes + 1] = code
            end
        end
    end
    file:close()

    M.aux_table = aux_table
    return aux_table
end

-- 将 UTF-8 字符串拆成单字数组。
-- Rime 候选文本是 UTF-8，不能直接用字节下标当作汉字位置。
local function split_chars(text)
    local chars = {}
    for _, codepoint in utf8.codes(text) do
        chars[#chars + 1] = utf8.char(codepoint)
    end
    return chars
end

-- 判断某个字是否有以 aux 开头的辅助码。
-- 既支持一码筛选（如 `n`），也支持完整两码筛选（如 `nu`）。
local function char_matches_prefix(aux_table, ch, aux)
    local codes = aux_table[ch]
    if not codes then
        return false
    end
    if type(codes) == "string" then
        return codes:sub(1, #aux) == aux
    end
    for _, code in ipairs(codes) do
        if code:sub(1, #aux) == aux then
            return true
        end
    end
    return false
end

-- 按顺序在候选中匹配一串辅助码。
-- 示例：
--   aux = "bd"
--   candidate = "事实"
--   实=bd 会被 `char_matches_prefix` 直接命中；此函数主要用于拆开匹配，
--   例如先匹配 `b`，再在后面的字里匹配 `d`。
local function match_subsequence(aux_table, chars, aux)
    local pos = 1
    for i = 1, #chars do
        local code = aux:sub(pos, pos)
        if code == "" then
            return true
        end
        if char_matches_prefix(aux_table, chars[i], code) then
            pos = pos + 1
        end
    end
    return pos > #aux
end

-- 兜底匹配：当没有更精确的“差异位置”匹配时使用。
-- 它会扫描候选里的所有字：
--   - 一码辅码：命中任意一个辅助码以该键开头的字；
--   - 两码辅码：可以命中某个字的完整辅码，也可以跨字按顺序匹配。
local function candidate_matches(aux_table, chars, aux)
    for i = 1, #chars do
        if char_matches_prefix(aux_table, chars[i], aux) then
            return true
        end
    end

    if #aux > 1 then
        return match_subsequence(aux_table, chars, aux)
    end
    return false
end

-- 找出一组候选中发生差异的位置。
-- 对整句候选来说，这能让筛选聚焦在真正需要消歧的字上，
-- 避免被后面无关的字误命中。
local function find_variant_positions(candidates)
    local positions = {}
    local max_len = 0
    for i = 1, #candidates do
        if #candidates[i].chars > max_len then
            max_len = #candidates[i].chars
        end
    end

    for pos = 1, max_len do
        local first = nil
        local differs = false
        for i = 1, #candidates do
            local ch = candidates[i].chars[pos]
            if ch then
                if first == nil then
                    first = ch
                elseif ch ~= first then
                    differs = true
                    break
                end
            end
        end
        if differs then
            positions[#positions + 1] = pos
        end
    end
    return positions
end

-- 选择第一组“同长度且存在差异”的候选。
-- Rime 通常会把可比较的整句候选放在一起，因此这里优先做整句级消歧，
-- 找不到合适分组时再回退到任意字匹配。
local function find_variant_group(candidates)
    local groups = {}
    local order = {}
    for i = 1, #candidates do
        local len = #candidates[i].chars
        if len > 0 then
            local group = groups[len]
            if not group then
                group = {}
                groups[len] = group
                order[#order + 1] = len
            end
            group[#group + 1] = candidates[i]
        end
    end

    for i = 1, #order do
        local group = groups[order[i]]
        if #group >= 2 then
            local positions = find_variant_positions(group)
            if #positions > 0 then
                return group, positions
            end
        end
    end
    return nil, nil
end

-- 只匹配候选中的指定位置，通常是同长度词组/整句候选里的差异位置。
local function candidate_matches_positions(aux_table, chars, aux, positions)
    for i = 1, #positions do
        local ch = chars[positions[i]]
        if ch and char_matches_prefix(aux_table, ch, aux) then
            return true
        end
    end
    if #aux > 1 then
        local selected = {}
        for i = 1, #positions do
            local ch = chars[positions[i]]
            if ch then
                selected[#selected + 1] = ch
            end
        end
        return match_subsequence(aux_table, selected, aux)
    end
    return false
end

function M.init(env)
    local config = env.engine.schema.config
    env.trigger_key = config:get_string("frost_aux_filter/trigger_key") or "`"

    -- 从辅码筛选输入中选词后，Rime 的 ctx.input 里仍然保留原始触发后缀
    -- （例如 `n）。提交前先移除它，否则辅码字母可能残留在 composition 中，
    -- 用户也可能需要再按一次空格。
    env.notifier = env.engine.context.select_notifier:connect(function(ctx)
        local trigger_pos = ctx.input:find(env.trigger_key, 1, true)
        if not trigger_pos then
            return
        end

        local trigger_pattern = escape_pattern(env.trigger_key)
        local input_without_aux = ctx.input:match("^(.-)" .. trigger_pattern)
        if input_without_aux and input_without_aux ~= "" then
            ctx.input = input_without_aux
            ctx:commit()
        end
    end)
end

function M.fini(env)
    if env.notifier then
        env.notifier:disconnect()
    end
end

function M.tags_match(seg, env)
    local aux = env.engine.context:get_property(char_aux_property)
    if aux == "" then return true end
    if not seg:has_tag("abc") then return false end
    seg.prompt = aux == waiting and " 〔逐字〕" or " 〔逐字 " .. aux .. "〕"
    return true
end

function M.func(input, env)
    local context = env.engine.context
    local char_aux = context:get_property(char_aux_property)
    if char_aux ~= "" and char_aux ~= waiting then
        local aux_table = load_aux_table()
        for cand in input:iter() do
            if (cand.type == "phrase" or cand.type == "user_phrase") and utf8.len(cand.text) == 1
                and char_matches_prefix(aux_table, cand.text, char_aux) then
                yield(cand)
            end
        end
        return
    end
    local input_code = context.input

    -- 普通输入的快速路径。这里仍然有 Lua filter 的透传成本，
    -- 但不会加载辅码表，也不会扫描候选文本。
    local trigger_pos = input_code:find(env.trigger_key, 1, true)
    if not trigger_pos then
        pass_through(input)
        return
    end

    local aux = input_code:sub(trigger_pos + #env.trigger_key):match("^([^,']+)") or ""
    aux = aux:sub(1, 2)
    if aux == "" then
        pass_through(input)
        return
    end

    local aux_table = load_aux_table()
    local next_candidate, state, cursor = input:iter()
    local candidates = {}
    local first_chars, width, remaining
    local differs = {}
    for cand in next_candidate, state, cursor do
        cursor = cand
        local chars = split_chars(cand.text)
        candidates[#candidates + 1] = { cand = cand, chars = chars }
        if not first_chars and #chars > 0 then
            first_chars, width, remaining = chars, #chars, #chars
        elseif #chars == width then
            for pos = 1, width do
                if not differs[pos] and chars[pos] ~= first_chars[pos] then
                    differs[pos] = true
                    remaining = remaining - 1
                end
            end
            if remaining == 0 then
                -- 最早出现的非空长度组已经确定胜出，所有位置也都已产生差异。
                -- 后续候选无法改变优先组或差异位置；沿用当前迭代器，按需筛选后页。
                local fallback = {}
                local function visit(candidate, candidate_chars)
                    local same_width = #candidate_chars == width
                    if (same_width or fallback) and candidate_matches(aux_table, candidate_chars, aux) then
                        if same_width then
                            fallback = nil
                            yield(candidate)
                        else
                            fallback[#fallback + 1] = candidate
                        end
                    end
                end
                for _, item in ipairs(candidates) do
                    visit(item.cand, item.chars)
                end
                candidates = nil
                for next_cand in next_candidate, state, cursor do
                    local text = next_cand.text
                    if fallback or utf8.len(text) == width then
                        visit(next_cand, split_chars(text))
                    end
                end
                -- 整组始终未命中才使用兜底；精确命中时不追加其他长度组。
                if fallback then
                    for _, candidate in ipairs(fallback) do
                        yield(candidate)
                    end
                end
                return
            end
        end
    end

    -- 第一组仍可能包含不变的位置，或不是最终胜出的组：保留原来的全局判定。
    local variant_group, variant_positions = find_variant_group(candidates)
    local has_variant_match = false
    if variant_group then
        for _, item in ipairs(variant_group) do
            if candidate_matches_positions(aux_table, item.chars, aux, variant_positions) then
                has_variant_match = true
                yield(item.cand)
            end
        end
    end
    if not has_variant_match then
        for _, item in ipairs(candidates) do
            if candidate_matches(aux_table, item.chars, aux) then
                yield(item.cand)
            end
        end
    end
end

return M
