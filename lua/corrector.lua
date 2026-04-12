--[[
	错音错字提示。
	示例：「给予」的正确读音是 ji yu，当用户输入 gei yu 时，在候选项的 comment 显示正确读音
	示例：「按耐」的正确写法是「按捺」，当用户输入「按耐」时，在候选项的 comment 显示正确写法

	关闭此 Lua 时，同时需要关闭 translator/spelling_hints，否则 comment 里都是拼音

	为了让这个 Lua 同时适配全拼与双拼，使用 `spelling_hints` 生成的 comment（全拼拼音）作为通用的判断条件。
	感谢大佬@[Shewer Lu](https://github.com/shewer)提供的思路。
	
	容错词在 cn_dicts/others.dict.yaml 中，有新增建议可以提个 issue
--]]

local M = {}

function M.init(env)
    local config = env.engine.schema.config
    env.keep_comment = config:get_bool('translator/keep_comments')
    local delimiter = config:get_string('speller/delimiter')
    if delimiter and #delimiter > 0 and delimiter:sub(1,1) ~= ' ' then
        env.delimiter = delimiter:sub(1,1)
    end
    env.name_space = env.name_space:gsub('^*', '')
    M.style = config:get_string(env.name_space) or '{comment}'
    M.corrections = {
        -- 错音
        ["hun dun"] = { text = "馄饨", comment = "hún tun" },
        ["zhu jiao"] = { text = "主角", comment = "zhǔ jué" },
        ["jiao se"] = { text = "角色", comment = "jué sè" },
        ["shui fu"] = { text = "说服", comment = "shuō fú" },
        ["dao hang"] = { text = "道行", comment = "dào heng" },
        ["mo yang"] = { text = "模样", comment = "mú yàng" },
        ["you mo you yang"] = { text = "有模有样", comment = "yǒu mú yǒu yàng" },
        ["yi mo yi yang"] = { text = "一模一样", comment = "yī mú yī yàng" },
        ["zhuang mo zuo yang"] = { text = "装模作样", comment = "zhuāng mú zuò yàng" },
        ["ren mo gou yang"] = { text = "人模狗样", comment = "rén mú gǒu yàng" },
        ["mo ban"] = { text = "模板", comment = "mú bǎn" },
        ["a mi tuo fo"] = { text = "阿弥陀佛", comment = "ē mí tuó fó" },
        ["na mo a mi tuo fo"] = { text = "南无阿弥陀佛", comment = "nā mó ē mí tuó fó" },
        ["nan wu a mi tuo fo"] = { text = "南无阿弥陀佛", comment = "nā mó ē mí tuó fó" },
        ["nan wu e mi tuo fo"] = { text = "南无阿弥陀佛", comment = "nā mó ē mí tuó fó" },
        ["bin lang"] = { text = "槟榔", comment = "bīng láng" },
        ["nong tang"] = { text = "弄堂", comment = "lòng táng" },
        ["xin kuan ti pang"] = { text = "心宽体胖", comment = "xīn kuān tǐ pán" },
        ["mai yuan"] = { text = "埋怨", comment = "mán yuàn" },
        ["xu yu wei she"] = { text = "虚与委蛇", comment = "xū yǔ wēi yí" },
        ["mu na"] = { text = "木讷", comment = "mù nè" },
        ["du le le"] = { text = "独乐乐", comment = "dú yuè lè" },
        ["zhong le le"] = { text = "众乐乐", comment = "zhòng yuè lè" },
        ["xun ma"] = { text = "荨麻", comment = "qián má" },
        ["qian ma zhen"] = { text = "荨麻疹", comment = "xún má zhěn" },
        ["mo ju"] = { text = "模具", comment = "mú jù" },
        ["cao zhi"] = { text = "草薙", comment = "cǎo tì" },
        ["cao zhi jing"] = { text = "草薙京", comment = "cǎo tì jīng" },
        ["cao zhi jian"] = { text = "草薙剑", comment = "cǎo tì jiàn" },
        ["jia ping ao"] = { text = "贾平凹", comment = "jiǎ píng wā" },
        ["xue fo lan"] = { text = "雪佛兰", comment = "xuě fú lán" },
        ["qiang jin"] = { text = "强劲", comment = "qiáng jìng" },
        ["tong ti"] = { text = "胴体", comment = "dòng tǐ" },
        ["li neng kang ding"] = { text = "力能扛鼎", comment = "lì néng gāng dǐng" },
        ["ya lv jiang"] = { text = "鸭绿江", comment = "yā lù jiāng" },
        ["da fu bian bian"] = { text = "大腹便便", comment = "dà fù pián pián" },
        ["ka bo zi"] = { text = "卡脖子", comment = "qiǎ bó zi" },
        ["chan he"] = { text = "掺和", comment = "chān huo" },
        ["can huo"] = { text = "掺和", comment = "chān huo" },
        ["can he"] = { text = "掺和", comment = "chān huo" },
        ["cheng zhi"] = { text = "称职", comment = "chèn zhí" },
        ["luo shi fen"] = { text = "螺蛳粉", comment = "luó sī fěn" },
        ["tai xing shan"] = { text = "太行山", comment = "tài háng shān" },
        ["jie si di li"] = { text = "歇斯底里", comment = "xiē sī dǐ lǐ" },
        ["fa xiao"] = { text = "发酵", comment = "fā jiào" }, 
        ["xiao mu jun"] = { text = "酵母菌", comment = "jiào mǔ jūn" },
        ["yin hong"] = { text = "殷红", comment = "yān hóng" },
        ["nuan he"] = { text = "暖和", comment = "nuǎn huo" },
        ["mo ling liang ke"] = { text = "模棱两可", comment = "mó léng liǎng kě" },
        ["pan yang hu"] = { text = "鄱阳湖", comment = "pó yáng hú" },
        ["bo jing"] = { text = "脖颈", comment = "bó gěng" },
        ["bo jing er"] = { text = "脖颈儿", comment = "bó gěng er" },
        ["niu pi xian"] = { text = "牛皮癣", comment = "niú pí xuǎn" },
        ["hua ban xian"] = { text = "花斑癣", comment = "huā bān xuǎn" },
        ["ti xian"] = { text = "体癣", comment = "tǐ xuǎn" },
        ["gu xian"] = { text = "股癣", comment = "gǔ xuǎn" },
        ["jiao xian"] = { text = "脚癣", comment = "jiǎo xuǎn" },
        ["zu xian"] = { text = "足癣", comment = "zú xuǎn" },
        ["jie zha"] = { text = "结扎", comment = "jié zā" },
        ["hai shen wei"] = { text = "海参崴", comment = "hǎi shēn wǎi" },
        ["hou pu"] = { text = "厚朴", comment = "hòu pò " },
        ["da wan ma"] = { text = "大宛马", comment = "dà yuān mǎ" },
        ["ci ya"] = { text = "龇牙", comment = "zī yá" },
        ["ci zhe ya"] = { text = "龇着牙", comment = "zī zhe yá" },
        ["ci ya lie zui"] = { text = "龇牙咧嘴", comment = "zī yá liě zuǐ" },
        ["tou pi xue"] = { text = "头皮屑", comment = "tóu pí xiè" },
        ["nuo da"] = { text = "偌大", comment = "偌(ruò)大" },
        ["yin jiu zhi ke"] = { text = "饮鸩止渴", comment = "饮鸩(zhèn)止渴" },
        ["yin jiu jie ke"] = { text = "饮鸩解渴", comment = "饮鸩(zhèn)解渴" },
        ["gong shang jiao zhi yu"] = { text = "宫商角徵羽", comment = "宫商角(jué)徵羽" },
        ["shan qi deng"] = { text = "氙气灯", comment = "氙(xiān)气灯" },
        ["shan qi da deng"] = { text = "氙气大灯", comment = "氙(xiān)气大灯" },
        ["shan qi shou dian tong"] = { text = "氙气手电筒", comment = "氙(xiān)气手电筒" },
        ["yin gai"] = { text = "应该", comment = "应(yīng)该" },
        ["nian tie"] = { text = "粘贴", comment = "粘(zhān)贴" },
        ["gao ju li"] = { text = "高句丽", comment = "高句(gōu)丽" },
        ["jiao dou shi"] = { text = "角斗士", comment = "角(jué)斗士" },
        ["suo sha mi"] = { text = "缩砂密", comment = "缩(sù)砂密" },
        ["wen bo"] = { text = "榅桲", comment = "wēn po" },
        ["bi ji"] = { text = "荸荠", comment = "bí qi" },
        ["rou yi"] = { text = "柔荑", comment = "柔荑(tí)" },
        ["rou yi hua xu"] = { text = "柔荑花序", comment = "柔荑(tí)花序" },
        ["shou ru rou yi"] = { text = "手如柔荑", comment = "手如柔荑(tí)" },
        ["wen ting jun"] = { text = "温庭筠", comment = "温庭筠(yún)" },
        ["san wei zhen huo"] = { text = "三昧真火", comment = "三昧(mèi)真火" },
        ["qing ping zhi mo"] = { text = "青𬞟之末", comment = "青𬞟(pín)之末" },
        ["qi yu qing ping zhi mo"] = { text = "起于青𬞟之末", comment = "起于青𬞟(pín)之末" },
        ["feng qi yu qing ping zhi mo"] = { text = "风起于青𬞟之末", comment = "风起于青𬞟(pín)之末" },
        ["you hui juan"] = { text = "优惠券", comment = "优惠券(quàn)" },
        ["gong quan"] = { text = "拱券", comment = "gǒng xuàn" },
        ["pu ru"] = { text = "哺乳", comment = "bǔ rǔ" },
        ["nao zu zhong"] = { text = "脑卒中", comment = "nǎo cù zhòng" },
        ["xie hu"] = { text = "潟湖", comment = "xì hú" },
        ["guo pu"] = { text = "果脯", comment = "guǒ fǔ" },
        ["rou pu"] = { text = "肉脯", comment = "ròu fǔ" },
        ["bai qi tun"] = { text = "白𬶨豚", comment = "bái jì tún" },
        -- 错字
        ["ceng jin"] = { text = "曾今", comment = "曾经" },
        ["an nai"] = { text = "按耐", comment = "按捺(nà)" },
        ["an nai bu zhu"] = { text = "按耐不住", comment = "按捺(nà)不住" },
        ["xue mai pen zhang"] = { text = "血脉喷张", comment = "血脉贲(bēn)张 | 血脉偾(fèn)张" },
        ["mo xie zuo"] = { text = "魔蝎座", comment = "摩羯(jié)座" },
        ["geng quan"] = { text = "梗犬", comment = "㹴犬" },
    }
end

function M.func(input, env)
    for cand in input:iter() do
        -- cand.comment 是目前输入的词汇的完整拼音
        local pinyin = cand.comment:match("^［(.-)］$")
        if pinyin and #pinyin > 0 then
            local correction_pinyin = pinyin
            if env.delimiter then
                correction_pinyin = correction_pinyin:gsub(env.delimiter,' ')
            end
            local c = M.corrections[correction_pinyin]
            if c and cand.text == c.text then
                cand:get_genuine().comment = string.gsub(M.style, "{comment}", c.comment)
            else
                if env.keep_comment then
                    cand:get_genuine().comment = string.gsub(M.style, "{comment}", pinyin)
                else
                    cand:get_genuine().comment = ""
                end
            end
        end
        yield(cand)
    end
end

return M
