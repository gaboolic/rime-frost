-- Rime 翻译插件初始化文件
-- 确保 trans 目录下的模块能正确互相引用

-- 获取当前文件所在目录
local trans_dir = debug.getinfo(1, "S").source:match("@(.*)/")
if trans_dir then
    -- 将 trans 目录添加到 package.path，使模块能互相引用
    package.path = package.path .. ";" .. trans_dir .. "/?.lua"
end


