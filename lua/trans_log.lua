-- 获取用户目录
local function get_user_dir()
    local os_name = package.config:sub(1,1) == '\\' and 'windows' or 'unix'
    if os_name == 'windows' then
        return os.getenv('APPDATA') .. '\\Rime'
    else
        return os.getenv('HOME') .. '/.config/rime'
    end
end

-- 日志文件的绝对路径
local log_path = get_user_dir() .. '/test-debug.log'

-- 测试日志路径是否可写
local test_log = io.open(log_path, "a")
if test_log then
    test_log:write("===== test.lua 开始记录日志 " .. os.date("%Y-%m-%d %H:%M:%S") .. " =====\n")
    test_log:close()
else
    -- 如果无法写入到用户配置目录，尝试写入到当前目录
    log_path = "./test-debug.log"
    test_log = io.open(log_path, "a")
    if test_log then
        test_log:write("===== test.lua 开始记录日志(当前目录) " .. os.date("%Y-%m-%d %H:%M:%S") .. " =====\n")
        test_log:close()
    end
end

-- 添加日志函数
local function info(message)
    local f = io.open(log_path, "a")
    if f then
        f:write(os.date("%Y-%m-%d %H:%M:%S") .. " [INFO] " .. message .. "\n")
        f:close()
    end
end

local function error(message)
    local f = io.open(log_path, "a")
    if f then
        f:write(os.date("%Y-%m-%d %H:%M:%S") .. " [ERROR] " .. message .. "\n")
        f:close()
    end
end

return {
    info = info,
    error = error
}