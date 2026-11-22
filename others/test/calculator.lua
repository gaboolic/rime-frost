-- 在仓库根目录运行：lua others/test/calculator.lua
local calculator = dofile('lua/calculator.lua')
local candidates

function Candidate(_, _, _, text, comment)
  assert(type(text) == 'string' and type(comment) == 'string')
  return { text = text, comment = comment }
end

function yield(candidate)
  candidates[#candidates + 1] = candidate
end

local function init(trigger)
  local config = { get_string = function(_, path)
    assert(path == 'calculator/trigger')
    return trigger
  end }
  local env = { name_space = '*calculator', engine = { schema = { config = config } } }
  calculator.init(env)
  return env
end

local function translate(env, input, tagged)
  local seg = {
    start = 0,
    _end = #input,
    has_tag = function(_, tag) return tagged and tag == 'calculator' end,
  }
  candidates = {}
  calculator.func(input, seg, env)
  return candidates
end

local default = init()
local custom = init('Calc')
assert(#translate(default, 'vdtl', false) == 0)
assert(#translate(default, 'v2+3', false) == 0)
assert(#translate(default, 'V2+3', false) == 0)
assert(#translate(default, 'V', true) == 0)
assert(#translate(custom, 'V2+3', true) == 0)

for _, input in ipairs({ 'V2+3', 'v2+3' }) do
  local result = translate(default, input, true)
  assert(#result == 2 and result[1].text == '5' and result[2].text == '2+3=5', input)
end
assert(translate(custom, 'Calc5!', true)[1].text == '120')
assert(translate(custom, 'calc5!', true)[1].text == '120')
assert(translate(default, 'V1==2', true)[1].text == 'false')
for _, input in ipairs({ 'Vfoo', 'V1+' }) do
  assert(translate(default, input, true)[1].comment == '解析失败', input)
end

print('calculator: OK')
