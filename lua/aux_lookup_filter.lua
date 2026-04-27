local M = {}

local function pass_through(input)
    for cand in input:iter() do
        yield(cand)
    end
end

local function load_aux_table()
    if M.aux_table then
        return M.aux_table
    end

    local aux_table = {}
    local file = io.open(rime_api.get_user_data_dir() .. "/lua/aux_code/moqi_aux_code.txt", "r")
    if not file then
        M.aux_table = aux_table
        return aux_table
    end

    for line in file:lines() do
        local ch, code = line:match("^([^=]+)=(.+)$")
        if ch and code and code ~= "" then
            local codes = aux_table[ch]
            if not codes then
                codes = {}
                aux_table[ch] = codes
            end
            codes[#codes + 1] = code
        end
    end
    file:close()

    M.aux_table = aux_table
    return aux_table
end

local function split_chars(text)
    local chars = {}
    for _, codepoint in utf8.codes(text) do
        chars[#chars + 1] = utf8.char(codepoint)
    end
    return chars
end

local function char_matches_prefix(aux_table, ch, aux)
    local codes = aux_table[ch]
    if not codes then
        return false
    end
    for _, code in ipairs(codes) do
        if code:sub(1, #aux) == aux then
            return true
        end
    end
    return false
end

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

local function candidate_matches(aux_table, text, aux)
    if text == "" or aux == "" then
        return false
    end

    local chars = split_chars(text)
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

function M.init(env)
    local config = env.engine.schema.config
    env.trigger_key = config:get_string("frost_aux_filter/trigger_key") or "`"
end

function M.func(input, env)
    local input_code = env.engine.context.input
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
    for cand in input:iter() do
        if candidate_matches(aux_table, cand.text, aux) then
            yield(cand)
        end
    end
end

return M
