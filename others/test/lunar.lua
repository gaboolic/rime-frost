-- 在仓库根目录运行：lua others/test/lunar.lua
local translator = dofile('lua/lunar.lua')
local candidates

function Candidate(_, start, stop, text)
    assert(start == 0 and stop > start and type(text) == 'string')
    return { text = text }
end

function yield(candidate)
    assert(candidate.quality == 999)
    candidates[#candidates + 1] = candidate.text
end

local function translate(input, tagged, pattern)
    local values = { lunar = 'nl', ['recognizer/patterns/gregorian_to_lunar'] = pattern }
    local config = { get_string = function(_, key) return values[key] end }
    local env = { name_space = '*lunar', engine = { schema = { config = config } } }
    local seg = {
        start = 0,
        _end = #input,
        has_tag = function(_, tag) return tagged and tag == 'gregorian_to_lunar' end,
    }
    candidates = {}
    translator(input, seg, env)
    return table.concat(candidates, '|')
end

local pattern = '^N[0-9]{1,8}'
for _, input in ipairs({ 'N', 'Nous', 'NVIDIA', 'N20240115' }) do
    assert(translate(input, false, pattern) == '', input)
end
for _, input in ipairs({ 'N95', 'N2026', 'N2024011', 'N202401159' }) do
    assert(translate(input, true, pattern) == '', input)
end
for _, input in ipairs({ 'N202401xx', 'N20241301', 'N20240431', 'N20230229', 'N18990101', 'N21010101' }) do
    assert(translate(input, true, pattern) == '无效日期', input)
end

local expected = '二〇二三年腊月初五|癸卯年（兔）腊月初五|2024年1月15日'
assert(translate('N20240115', true, pattern) == expected)
assert(translate('D20240115', true, '^D[0-9]{1,8}') == expected)
assert(translate('N20240115', false, nil) == '')
assert(translate('N20240229', true, pattern):match('2024年2月29日$'))
assert(translate('N19000229', true, pattern) == '无效日期')
assert(translate('N21000229', true, pattern) == '无效日期')

-- 按香港天文台对照表核对世纪年、前导零、闰月与跨年衔接。
local historical_dates = {
    N19010218 = '一九〇〇年腊月三十',
    N19010219 = '一九〇一年正月初一',
    N19270104 = '一九二六年腊月初一',
    N19351226 = '一九三五年腊月初一',
    N19460104 = '一九四五年腊月初二',
    N19550521 = '一九五五年闰三月三十',
    N19560211 = '一九五五年腊月三十',
    N20000229 = '二〇〇〇年正月廿五',
    N20080109 = '二〇〇七年腊月初二',
    N20331222 = '二〇三三年闰冬月初一',
    N20340218 = '二〇三三年腊月三十',
    N20660125 = '二〇六五年腊月三十',
    N20690122 = '二〇六八年腊月三十',
    N20790201 = '二〇七八年腊月三十',
    N21000301 = '二一〇〇年正月廿一',
    N21001231 = '二一〇〇年腊月初一',
}
for input, lunar in pairs(historical_dates) do
    local actual = translate(input, true, pattern):match('^[^|]+')
    assert(actual == lunar, input .. ': ' .. tostring(actual))
end

-- 遍历全部公历有效日期，必须逐日产生三个候选，不能漏掉农历年末。
local month_days = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
local count = 0
for year = 1900, 2100 do
    for month, normal_days in ipairs(month_days) do
        local leap_day = month == 2 and year % 4 == 0 and year ~= 1900 and year ~= 2100
        for day = 1, normal_days + (leap_day and 1 or 0) do
            local input = string.format('N%04d%02d%02d', year, month, day)
            translate(input, true, pattern)
            assert(#candidates == 3, input)
            assert(candidates[3] == string.format('%d年%d月%d日', year, month, day), input)
            count = count + 1
        end
    end
end
assert(count == 73414)

os.date = function(format)
    assert(format == '%Y%m%d')
    return '20240115'
end
assert(translate('nl', false, nil) == expected)
print('lunar: OK')
