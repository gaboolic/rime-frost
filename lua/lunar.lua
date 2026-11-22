--[[
	Lua 阿拉伯数字转中文实现 https://blog.csdn.net/lp12345678910/article/details/121396243
	农历功能复制自 https://github.com/boomker/rime-fast-xhup
--]]
--
-- 农历，可在方案中配置触发关键字。

-- 数字转中文：

local numerical_units = {
    "",
    "十",
    "百",
    "千",
    "万",
    "十",
    "百",
    "千",
    "亿",
    "十",
    "百",
    "千",
    "兆",
    "十",
    "百",
    "千",
}

local numerical_names = {
    "零",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
}

local function convert_arab_to_chinese(number)
    local n_number = tonumber(number)
    assert(n_number, "传入参数非正确number类型!")

    -- 0 ~ 9
    if n_number < 10 then
        return numerical_names[n_number + 1]
    end
    -- 一十九 => 十九
    if n_number < 20 then
        local digit = string.sub(n_number, 2, 2)
        if digit == "0" then
            return "十"
        else
            return "十" .. numerical_names[digit + 1]
        end
    end

    --[[
        1. 最大输入9位
            超过9位，string的len加2位（因为有.0的两位）
            零 ~ 九亿九千九百九十九万九千九百九十九
            0 ~ 999999999
        2. 最大输入14位（超过14位会四舍五入）
            零 ~ 九十九兆九千九百九十九亿九千九百九十九万九千九百九十九万
            0 ~ 99999999999999
    --]]
    local len_max = 9
    local len_number = string.len(number)
    assert(
        len_number > 0 and len_number <= len_max,
        "传入参数位数" .. len_number .. "必须在(0, " .. len_max .. "]之间！"
    )

    -- 01，数字转成表结构存储
    local numerical_tbl = {}
    for i = 1, len_number do
        numerical_tbl[i] = tonumber(string.sub(n_number, i, i))
    end

    local pre_zero = false
    local result = ""
    for index, digit in ipairs(numerical_tbl) do
        local curr_unit = numerical_units[len_number - index + 1]
        local curr_name = numerical_names[digit + 1]
        if digit == 0 then
            if not pre_zero then
                result = result .. curr_name
            end
            pre_zero = true
        else
            result = result .. curr_name .. curr_unit
            pre_zero = false
        end
    end
    result = string.gsub(result, "零+$", "")
    return result
end

-- 农历：

-- 天干名称
local cTianGan = {
    "甲",
    "乙",
    "丙",
    "丁",
    "戊",
    "己",
    "庚",
    "辛",
    "壬",
    "癸",
}

-- 地支名称
local cDiZhi = {
    "子",
    "丑",
    "寅",
    "卯",
    "辰",
    "巳",
    "午",
    "未",
    "申",
    "酉",
    "戌",
    "亥",
}

-- 属相名称
local cShuXiang = {
    "鼠",
    "牛",
    "虎",
    "兔",
    "龙",
    "蛇",
    "马",
    "羊",
    "猴",
    "鸡",
    "狗",
    "猪",
}

-- 农历日期名
local cDayName = {
    "初一",
    "初二",
    "初三",
    "初四",
    "初五",
    "初六",
    "初七",
    "初八",
    "初九",
    "初十",
    "十一",
    "十二",
    "十三",
    "十四",
    "十五",
    "十六",
    "十七",
    "十八",
    "十九",
    "二十",
    "廿一",
    "廿二",
    "廿三",
    "廿四",
    "廿五",
    "廿六",
    "廿七",
    "廿八",
    "廿九",
    "三十",
}

-- 农历月份名
local cMonName = {
    "正月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "冬月",
    "腊月",
}

-- 农历数据（1899 年起）；以下跨年缺日的五条记录按香港天文台对照表校正：
-- https://www.hko.gov.hk/tc/gts/time/conversion1_text.htm
local wNongliData = {
    "AB500D2",
    "4BD0883",
    "4AE00DB",
    "A5700D0",
    "54D0581",
    "D2600D8",
    "D9500CC",
    "655147D",
    "56A00D5",
    "9AD00CA",
    "55D027A",
    "4AE00D2",
    "A5B0682",
    "A4D00DA",
    "D2500CE",
    "D25157E",
    "B5500D6",
    "56A00CC",
    "ADA027B",
    "95B00D3",
    "49717C9",
    "49B00DC",
    "A4B00D0",
    "B4B0580",
    "6A500D8",
    "6D400CD",
    "AB5147C",
    "2B600D5",
    "95700CA",
    "52F027B",
    "49700D2",
    "6560682",
    "D4A00D9",
    "EA500CE",
    "6A9157E",
    "5AD00D6",
    "2B600CC",
    "86E137C",
    "92E00D3",
    "C8D1783",
    "C9500DB",
    "D4A00D0",
    "D8A167F",
    "B5500D7",
    "56A00CD",
    "A5B147D",
    "25D00D5",
    "92D00CA",
    "D2B027A",
    "A9500D2",
    "B550781",
    "6CA00D9",
    "B5500CE",
    "535157F",
    "4DA00D6",
    "A5B00CB",
    "457137C", -- 1955
    "52B00D4",
    "A9A0883",
    "E9500DA",
    "6AA00D0",
    "AEA0680",
    "AB500D7",
    "4B600CD",
    "AAE047D",
    "A5700D5",
    "52600CA",
    "F260379",
    "D9500D1",
    "5B50782",
    "56A00D9",
    "96D00CE",
    "4DD057F",
    "4AD00D7",
    "A4D00CB",
    "D4D047B",
    "D2500D3",
    "D550883",
    "B5400DA",
    "B6A00CF",
    "95A1680",
    "95B00D8",
    "49B00CD",
    "A97047D",
    "A4B00D5",
    "B270ACA",
    "6A500DC",
    "6D400D1",
    "AF40681",
    "AB600D9",
    "93700CE",
    "4AF057F",
    "49700D7",
    "64B00CC",
    "74A037B",
    "EA500D2",
    "6B50883",
    "5AC00DB",
    "AB600CF",
    "96D0580",
    "92E00D8",
    "C9600CD",
    "D95047C",
    "D4A00D4",
    "DA500C9",
    "755027A",
    "56A00D1",
    "ABB0781",
    "25D00DA",
    "92D00CF",
    "CAB057E",
    "A9500D6",
    "B4A00CB",
    "BAA047B",
    "AD500D2",
    "55D0983",
    "4BA00DB",
    "A5B00D0",
    "5171680",
    "52B00D8",
    "A9300CD",
    "795047D",
    "6AA00D4",
    "AD500C9",
    "5B5027A",
    "4B600D2",
    "96E0681",
    "A4E00D9",
    "D2600CE",
    "EA6057E",
    "D5300D5",
    "5AA00CB",
    "76A037B",
    "96D00D3",
    "4AF0B83", -- 2033
    "4AD00DB",
    "A4D00D0",
    "D0B1680",
    "D2500D7",
    "D5200CC",
    "DD4057C",
    "B5A00D4",
    "56D00C9",
    "55B027A",
    "49B00D2",
    "A570782",
    "A4B00D9",
    "AA500CE",
    "B25157E",
    "6D200D6",
    "ADA00CA",
    "4B6137B",
    "93700D3",
    "49F08C9",
    "49700DB",
    "64B00D0",
    "68A1680",
    "EA500D7",
    "6AA00CC",
    "A6C147C",
    "AAE00D4",
    "92E00CA",
    "D2E0379",
    "C9600D1",
    "D550781",
    "D4A00D9",
    "DA500CD", -- 2065
    "5D5057E",
    "56A00D6",
    "A6D00CB", -- 2068
    "55D047B",
    "52D00D3",
    "A9B0883",
    "A9500DB",
    "B4A00CF",
    "B6A067F",
    "AD500D7",
    "55A00CD",
    "ABA047C",
    "A5B00D4", -- 2078
    "52B00CA",
    "B27037A",
    "69300D1",
    "7330781",
    "6AA00D9",
    "AD500CE",
    "4B5157E",
    "4B600D6",
    "A5700CB",
    "54E047C",
    "D1600D2",
    "E960882",
    "D5200DA",
    "DAA00CF",
    "6AA167F",
    "56D00D7",
    "4AE00CD",
    "A9D047D",
    "A2D00D4",
    "D1500C9",
    "F250279",
    "D5200D1",
}

-- 解出正月到腊月的 12 位大小月标识（含前导零）、闰月和春节日期。
local function decode_lunar_year(data)
    local mask = tonumber(data:sub(1, 3), 16)
    local month_days = {}
    for month = 12, 1, -1 do
        month_days[month] = 29 + mask % 2
        mask = math.floor(mask / 2)
    end
    local leap_month = tonumber(data:sub(5, 5), 16)
    if leap_month > 0 then
        local leap_days = 29 + tonumber(data:sub(4, 4), 16)
        table.insert(month_days, leap_month + 1, leap_days)
    end
    local new_year = tonumber(data:sub(6, 7), 16)
    return month_days, leap_month, new_year
end

local function days_in_year(year)
    return (year % 400 == 0 or (year % 4 == 0 and year % 100 ~= 0)) and 366 or 365
end

local gregorian_month_days = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
local function days_in_month(year, month)
    if month == 2 and days_in_year(year) == 366 then
        return 29
    end
    return gregorian_month_days[month]
end

local function day_of_year(year, month, day)
    for i = 1, month - 1 do
        day = day + days_in_month(year, i)
    end
    return day
end

local function new_year_day(year, mmdd)
    return day_of_year(year, math.floor(mmdd / 100), mmdd % 100)
end

-- 公历转农历，支持转化范围公元1900-2100年
-- 公历日期 Gregorian:格式 YYYYMMDD
-- <返回值>带干支生肖的农历日期、中文农历日期、公历日期；无效时返回 nil
local function Date2LunarDate(Gregorian)
    local year, month, day = Gregorian:match("^(%d%d%d%d)(%d%d)(%d%d)$")
    if not year then
        return nil
    end
    local Year, Month, Day = tonumber(year), tonumber(month), tonumber(day)
    -- 1899 年的数据只用于换算 1900 年春节之前的日期。
    if Year < 1900 or Year > 2100 or Month < 1 or Month > 12 or Day < 1 or Day > days_in_month(Year, Month) then
        return nil
    end
    local LunarDate3 = Year .. "年" .. Month .. "月" .. Day .. "日"
    local LYear = Year
    local pos = Year - 1899 + 1
    local month_days, leap_month, new_year = decode_lunar_year(wNongliData[pos])
    local ordinal = day_of_year(Year, Month, Day)
    if Month * 100 + Day < new_year then
        LYear = Year - 1
        month_days, leap_month, new_year = decode_lunar_year(wNongliData[pos - 1])
        ordinal = ordinal + days_in_year(LYear)
    end
    local LDay = ordinal - new_year_day(LYear, new_year) + 1
    local LunarMonth
    for i, days in ipairs(month_days) do
        if LDay <= days then
            if leap_month > 0 and i == leap_month + 1 then
                LunarMonth = "闰" .. cMonName[leap_month]
            else
                local month = leap_month > 0 and i > leap_month and i - 1 or i
                LunarMonth = cMonName[month]
            end
            break
        end
        LDay = LDay - days
    end
    if not LunarMonth or LDay < 1 then
        return nil
    end

    local _nis = tostring(LYear)
    local _LunarYears = ""
    for i = 1, _nis:len() do
        local _ni_digit = tonumber(_nis:sub(i, i))
        _LunarYears = _LunarYears .. convert_arab_to_chinese(_ni_digit)
    end

    local LunarYear = string.gsub(_LunarYears, "零", "〇")
    local LunarDate = cTianGan[math.fmod(LYear - 4, 10) + 1]
        .. cDiZhi[math.fmod(LYear - 4, 12) + 1]
        .. "年（"
        .. cShuXiang[math.fmod(LYear - 4, 12) + 1]
        .. "）"
        .. LunarMonth
        .. cDayName[LDay]

    local LunarDate2 = LunarYear .. "年" .. LunarMonth .. cDayName[LDay]

    return LunarDate, LunarDate2, LunarDate3
end

-- 农历
-- 从 lunar: nl 获取农历触发关键字（双拼默认为 lunar）
-- 从 recognizer/patterns/gregorian_to_lunar 获取第 2 个字符作为公历转农历的触发前缀，默认为 N
local function translator(input, seg, env)
    env.lunar_key_word = env.lunar_key_word or
        (env.engine.schema.config:get_string(env.name_space:gsub('^*', '')) or 'nl')
    env.gregorian_to_lunar = env.gregorian_to_lunar or
        (env.engine.schema.config:get_string('recognizer/patterns/gregorian_to_lunar') or ''):sub(2, 2)

    local gregorian
    if input == env.lunar_key_word then
        gregorian = os.date("%Y%m%d")
    elseif env.gregorian_to_lunar ~= '' and seg:has_tag('gregorian_to_lunar')
        and input:sub(1, 1) == env.gregorian_to_lunar and #input == 9 then
        -- 日期没输满时不生成候选，保留正常的英文和数字输入。
        gregorian = input:sub(2)
    else
        return
    end

    local date1, date2, date3 = Date2LunarDate(gregorian)
    for _, text in ipairs(date1 and { date2, date1, date3 } or { "无效日期" }) do
        local cand = Candidate("", seg.start, seg._end, text, "")
        cand.quality = 999
        yield(cand)
    end
end

local function yield_cand(seg, text)
    local cand = Candidate('', seg.start, seg._end, text, '')
    cand.quality = 1000000
    yield(cand)
end

return translator