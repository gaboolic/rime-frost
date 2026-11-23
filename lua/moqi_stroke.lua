-- One unknown stroke is resolved on demand, without expanding the stroke prism.
local stroke_keys = { "h", "s", "p", "n", "z" }
local stroke_glyphs = { h = "一", s = "丨", p = "丿", n = "丶", z = "乛", x = "＊" }
local accepted, noop = 1, 2

local processor = {}
function processor.func(key, env)
  if key:release() or key:ctrl() or key:alt() or key:super() or key:shift() then
    return noop
  end
  local ctx = env.engine.context
  local composing = ctx:is_composing()
  if key.keycode == 0x27 then  -- apostrophe: close the active stroke segment
    local seg = composing and ctx.composition:back()
    if seg and seg:has_tag("abc") and ctx:has_menu()
        and not ctx:get_option("ascii_mode") then
      local auto_commit = ctx:get_option("_auto_commit")
      if auto_commit then
        local index = seg.selected_index
        ctx:set_option("_auto_commit", false)
        -- Changing an option can rebuild the menu and reset its highlight.
        if index > 0 then
          local current = ctx.composition:back()
          if current and current.menu and current.menu:prepare(index + 1) > index then
            current.selected_index = index
          end
        end
      end
      ctx:confirm_current_selection()
      if auto_commit then ctx:set_option("_auto_commit", true) end
    end
    -- No-op at idle, with no matches, or after an already closed segment.
    return accepted
  end
  if key.keycode == 0x78 then  -- x: bound the number of queries per segment
    local seg = composing and ctx.composition:back()
    if seg and seg:has_tag("abc")
        and ctx.input:sub(seg.start + 1, seg._end):find("x", 1, true) then
      return accepted
    end
  end
  return noop
end

local translator = {}
function translator.init(env)
  env.stroke = Component.Translator(env.engine, "", "table_translator@translator")
end

function translator.func(input, seg, env)
  local pos = input:find("x", 1, true)
  if not pos or input:find("x", pos + 1, true) or not seg:has_tag("abc") then
    return
  end
  local prefix, suffix = input:sub(1, pos - 1), input:sub(pos + 1)
  local preedit = input:gsub("[hspnzx]", stroke_glyphs)
  local streams, seen = {}, {}
  for _, stroke in ipairs(stroke_keys) do
    local translation = env.stroke:query(prefix .. stroke .. suffix, seg)
    if translation then
      local advance, state = translation:iter()
      streams[#streams + 1] = { advance = advance, state = state, cand = advance(state) }
    end
  end
  -- Merge lazy streams; exact matches precede prefix completions.
  while true do
    local best
    for _, stream in ipairs(streams) do
      local cand = stream.cand
      if cand and (not best
          or (cand.type ~= "completion" and best.cand.type == "completion")
          or (cand.type == best.cand.type and cand.quality > best.cand.quality)) then
        best = stream
      end
    end
    if not best then return end
    local cand = best.cand
    if not seen[cand.text] then
      seen[cand.text] = true
      cand.preedit = preedit
      yield(cand)
    end
    best.cand = best.advance(best.state)
  end
end

return { processor = processor, translator = translator }
