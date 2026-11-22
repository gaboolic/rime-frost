-- 在仓库根目录运行：lua others/test/aux_lookup_filter.lua
local filter = dofile('lua/aux_lookup_filter.lua')
local data = { '甲=a', '乙=r', '丙=b', '丁=d', '晚=r', '中=z', '敏=rb', '晚=xy' }
local opens = 0
local original_open = io.open
rime_api = { get_user_data_dir = function() return 'mock' end }
io.open = function(path, mode)
    assert(path == 'mock/lua/aux_code/moqi_aux_code.txt' and mode == 'r')
    opens = opens + 1
    return {
        lines = function()
            local i = 0
            return function() i = i + 1; return data[i] end
        end,
        close = function() end,
    }
end

yield = coroutine.yield
local function run(texts, suffix, char_aux)
    local consumed = 0
    local started = false
    local input = { iter = function()
        assert(not started, '候选流只能迭代一次')
        started = true
        return function(_, last)
            local i = last and last.index + 1 or 1
            if texts[i] then
                consumed = consumed + 1
                return { index = i, text = texts[i], type = 'phrase' }
            end
        end, nil, nil
    end }
    local context = { input = 'x' .. suffix, get_property = function() return char_aux or '' end }
    local env = { trigger_key = '`', engine = { context = context } }
    local co = coroutine.create(function() filter.func(input, env) end)
    return function()
        local ok, cand = coroutine.resume(co)
        assert(ok, cand)
        return cand and cand.text, consumed
    end
end

local function collect(next_text)
    local result = {}
    while true do
        local text = next_text()
        if not text then return table.concat(result, '|') end
        result[#result + 1] = text
    end
end

assert(collect(run({ '甲', '乙' }, '')) == '甲|乙')
assert(collect(run({ '甲', '乙' }, '`')) == '甲|乙')
assert(opens == 0)

-- 首组的每个位置已经出现差异：首个命中不必等尾部，后页仍能取到命中。
local candidates = { '甲', '乙', '乙丁' }
for _ = 1, 500 do candidates[#candidates + 1] = '丙丁' end
candidates[#candidates + 1] = '晚'
local next_text = run(candidates, '`r')
local text, consumed = next_text()
assert(text == '乙' and consumed == 2)
assert(collect(next_text) == '晚')
assert(opens == 1)
io.open = original_open

-- 精确命中在后页时丢弃先看到的兜底；整组无精确命中才返回兜底。
assert(collect(run({ '甲', '丙', '乙丁', '晚丙', '晚' }, '`r')) == '晚')
assert(collect(run({ '甲', '丙', '乙丁', '晚丙' }, '`r')) == '乙丁|晚丙')

-- 差异位置尚未全部确定、以及最早长度组没有差异，仍按原有优先级筛选。
assert(collect(run({ '中甲', '中丙', '中丁', '丙' }, '`b')) == '中丙')
assert(collect(run({ '中甲', '中丙', '中丁' }, '`z')) == '中甲|中丙|中丁')
assert(collect(run({ '甲甲', '乙', '丙', '甲甲' }, '`r')) == '乙')
assert(collect(run({ '甲丙', '甲丁', '乙丙', '晚丁' }, '`r')) == '乙丙|晚丁')
assert(collect(run({ '甲丙', '乙丁', '晚丙', '敏', '乙丙' }, '`rb')) == '晚丙|乙丙')
assert(collect(run({ '', '甲', '乙' }, '`r')) == '乙')
assert(collect(run({ '甲', '丙' }, '`r')) == '')
assert(collect(run({ '甲', '晚' }, '`xy')) == '晚')
-- 逐字模式仅输出命中的单字，不改变现有候选对象及迭代顺序。
assert(collect(run({ '甲乙', '甲', '乙', '晚' }, '', 'r')) == '乙|晚')
assert(collect(run({ '甲乙', '甲', '乙' }, '', '!')) == '甲乙|甲|乙')
assert(collect(run({ '乙', '晚' }, '', 'zz')) == '')
print('aux_lookup_filter: OK')
