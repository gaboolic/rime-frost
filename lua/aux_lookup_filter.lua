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

local function collect_candidates(input)
    local candidates = {}
    for cand in input:iter() do
        candidates[#candidates + 1] = {
            cand = cand,
            chars = split_chars(cand.text),
        }
    end
    return candidates
end

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
    local candidates = collect_candidates(input)
    local variant_group, variant_positions = find_variant_group(candidates)
    local yielded = {}
    local has_variant_match = false

    if variant_group and variant_positions then
        for i = 1, #variant_group do
            local item = variant_group[i]
            if candidate_matches_positions(aux_table, item.chars, aux, variant_positions) then
                yielded[item] = true
                has_variant_match = true
                yield(item.cand)
            end
        end
    end

    for i = 1, #candidates do
        local item = candidates[i]
        if not yielded[item] then
            if (not has_variant_match) and candidate_matches(aux_table, item.cand.text, aux) then
                yield(item.cand)
            end
        end
    end
end

return M
