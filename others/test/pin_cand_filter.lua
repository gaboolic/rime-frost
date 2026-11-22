-- 在仓库根目录运行：lua others/test/pin_cand_filter.lua
local filter = dofile('lua/pin_cand_filter.lua')

local function run(targets, words)
    local output = {}
    yield = function(candidate) output[#output + 1] = candidate.text end
    local position = 0
    local input = { iter = function()
        return function()
            position = position + 1
            if words[position] then return { text = words[position], preedit = 'a' } end
        end
    end }
    local env = {
        pin_cands = { a = targets },
        engine = { context = {
            get_option = function(_, option) return option == 'pin_cand' end,
            get_preedit = function() return { text = 'a' } end,
        } },
    }
    filter.func(input, env)
    return table.concat(output, '|')
end

-- 同一个目标出现两次，不能提前停止查找第二个目标。
assert(run({ '啊', '阿' }, { '啊', '啊', '按', '阿', '爱' }) == '啊|阿|按|爱')
-- 用户有真实的一键自定义短语时仍可置顶。
assert(run({ '啊', '爱好' }, { '按', '啊', '爱好' }) == '啊|爱好|按')
print('pin_cand_filter: OK')
