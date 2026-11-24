-- 以词定字
-- 原脚本 https://github.com/BlindingDark/rime-lua-select-character
-- 删除了默认按键 [ ]，和方括号翻页冲突，需要在 key_binder 下指定才能生效
-- 20230526195910 不再错误地获取commit_text，而是直接获取get_selected_candidate().text
-- 20240128141207 重写：将读取设置移动到 init 方法中；简化中文取字方法；预先判断候选存在与否，无候选取 input
-- 20240508111725 当候选字数为 1 时，快捷键使该字上屏

local select = {}

function select.init(env)
    local config = env.engine.schema.config
    env.first_key = config:get_string('key_binder/select_first_character')
    env.last_key = config:get_string('key_binder/select_last_character')
end

function select.func(key, env)
    local engine = env.engine
    local context = env.engine.context

    if
        not key:release()
        -- 仅要求存在候选菜单：URL 识别态下 is_composing() 也为 true，
        -- 若不过滤会吞掉 IPv6 地址中的 '[' 并上屏单个字母。
        and context:has_menu()
        and (env.first_key or env.last_key)
    then
        local selected_candidate = context:get_selected_candidate()
        if not selected_candidate then return 2 end
        local text = selected_candidate.text
        if utf8.len(text) > 1 then
            if (key:repr() == env.first_key) then
                engine:commit_text(text:sub(1, utf8.offset(text, 2) - 1))
                context:clear()
                return 1
            elseif (key:repr() == env.last_key) then
                engine:commit_text(text:sub(utf8.offset(text, -1)))
                context:clear()
                return 1
            end
        else
            if key:repr() == env.first_key or key:repr() == env.last_key then
                engine:commit_text(text)
                context:clear()
                return 1
            end
        end
    end
    return 2
end

return select
