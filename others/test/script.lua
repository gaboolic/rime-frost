print("script begins!")

print("hello world in lua!")

--- rimeac.setup_rime(app_name, shared_data_dir, user_data_dir, log_dir)
rimeac.setup_rime("rimeac.lua", "./shared", "./usr", "./log")
--- rimeac.init_rime()  no params, deploy
rimeac.init_rime()

--- add a session
--- rimeac.add_session() no params
rimeac.add_session()
--- print sessions list
--- rimeac.print_sessions() no params
rimeac.print_sessions()

rimeac.add_session()
rimeac.print_sessions()

rimeac.add_session()

--- select schema by schema_id
--- rimeac.select_schema(schema_id)
rimeac.select_schema("rime_frost")
rimeac.print_sessions()

--- kill a session by index, which is the map index of sessions, always >= 1
--- rimeac.kill_session(session_index) index >= 1
rimeac.kill_session(1)
rimeac.print_sessions()

--- switch to a session by index
--- rimeac.switch_session(session_index) index >= 1
rimeac.switch_session(2)

--- get session_id by index, if it doesn't exists, return 0
--- rimeac.get_session(session_index) index >= 1
local id = rimeac.get_session(10)
print(string.format("get_session id: 0x%x", id))
rimeac.print_sessions()

rimeac.select_schema("rime_frost")
rimeac.print_sessions()

--- set option to current session
--- rimeac.set_option(option_name, bool value)
rimeac.set_option("traditionalization", false)
--- rimeac.set_option("zh_trad", false)

--- get index of current session
local cindex = rimeac.get_index_of_current_session()
print("current session index: ", cindex)

local sid = rimeac.get_session(3)
local sidx = rimeac.get_index_of_session(sid)
print("specific session index: ", sidx)

--- simulate key sequence to current session
--- rimeac.simulate_keys(key_sequence)
local test_cases = {
    {keys = "ceshi", expected = "测试"},
    {keys = "pinyin", expected = "拼音"},
    {keys = "gegeguojiadouyougegeguojiadeguoge", expected = "各个国家都有各个国家的国歌"},
    {keys = "gegeguojia", expected = "各个国家"},
    {keys = "paocaichaowuhuarou", expected = "泡菜炒五花肉"},
    {keys = "zongxianguige", expected = "总线规格"},
    {keys = "tushuguandecangshugezhonggeyang", expected = "图书馆的藏书各种各样"},
    {keys = "dukaqibiaopeiliuheyidukaqichacao", expected = "读卡器标配六合一读卡器插槽"},
    {keys = "dukaqibiaopei", expected = "读卡器标配"},
    {keys = "liuheyidukaqichacao", expected = "六合一读卡器插槽"},
    {keys = "diercizaoshoudaguimojinfan", expected = "第二次遭受大规模进犯"},
    {keys = "diaoyuyaodaodaoshangdiao", expected = "钓鱼要到岛上钓"},
    {keys = "gaodewohaihuaiyishibushizijidacuoguanjiancile", expected = "搞的我还怀疑是不是自己打错关键词了"},
    {keys = "zhonghuaminzudeziranchongbaiyuzuxianchongbai", expected = "中华民族的自然崇拜与祖先崇拜"},
    {keys = "keyijixutianjiagengduoceshianli", expected = "可以继续添加更多测试案例"},
    {keys = "buranzhenlandedong", expected = "不然真懒得动"},
    {keys = "natianzhichileyangshiqiehuan", expected = "哪天支持了样式切换"},
    {keys = "jiukeyishunbianbakuaijiejianbangshang", expected = "就可以顺便把快捷键绑上"},
    {keys = "gaiyangshikuaiduole", expected = "改样式快多了"},
    {keys = "woyejiuleyixiele", expected = "我也就乐意写了"},
    {keys = "buganzaiqianbuganzaihou", expected = "不敢在前不敢在后"},
    {keys = "natianzhichizhegegongneng", expected = "那天支持这个功能"},
    {keys = "natianzhichileyidiandongxi", expected = "那天只吃了一点东西"},
    {keys = "natianzhichileyidianpingguo", expected = "那天只吃了一点苹果"},
    {keys = "zhichileyigepingguo", expected = "只吃了一点苹果"},
    {keys = "zhichilenidewenzhang", expected = "支持了你的文章"},
    {keys = "zhichileyidunfan", expected = "支持了一顿饭"},
    { keys = "tamenzaigongyuanlisanbushikandaoleyizhichangjinglu", expected = "他们在公园里散步是看到了一只长颈鹿"},
    { keys = "tamenzaigongyuanlisanbu", expected = "他们在公园里散步"},
    { keys = "kandaoleyizhichangjinglu", expected = "看到了一只长颈鹿"},
    { keys = "tadeyanjianghenyoushuofulidedaolequanchangdezhangsheng", expected = "他的演讲很有说服力得到了全场的掌声"},
    { keys = "zhegewentidedaanyinggaizaikebenshang", expected = "这个问题的答案应该在课本上"},
    { keys = "tamenyizhizainulixuexitigaozijidejinengshuiping", expected = "他们一直在努力学习提高自己的技能水平"},
    { keys = "tadejialiyouliangzhikeaidexiaomaoheyitiaocongmingdegou", expected = "他的家里有两只可爱的小猫和一条聪明的狗"},
    { keys = "zhejianyifudeyansehekuanshidouhenshiheni", expected = "这件衣服的颜色和款式都很适合你"},
    { keys = "tamenzuotianyijingyuyuelemingtiandehuiyi", expected = "他们昨天已经预约了明天的会议"},
    { keys = "woyaobazhegewentipaogeinininengbunengbangwojiedayixia", expected = "我要把这个问题抛给你你能不能帮我解答一下"},
    { keys = "zhexiekaotidedaandouyijinggongbule", expected = "这些考题的答案都已经公布了"},
    { keys = "nideyijianwohuirenzhenkaolvde", expected = "你的意见我会认真考虑的"},
    { keys = "womenxuexiaodexueshengshuliangyijingchaoguoleyiqianren", expected = "我们学校的学生数量已经超过了一千人"},
    { keys = "zhexietushuguandecangshufengfuduocai", expected = "这些图书馆的藏书丰富多彩"},
    { keys = "tadejianyibucuodanshishiqilaikenenghuiyudaokunnan", expected = "他的建议不错但实施起来可能会遇到困难"},
    { keys = "zhegehuiyiyinggaitiqiantongzhisuoyoucanyuzhe", expected = "这个会议应该提前通知所有参与者"},
    { keys = "tamendefangzihendadanshiweizhibutailixiang", expected = "他们的房子很大但是位置不太理想"},
    { keys = "zhegexiangmudezhixingshijianxuyaojinyibutaolun", expected = "这个项目的执行时间需要进一步讨论"},
    { keys = "nideyijianwomenhuirenzhenkaolvde", expected = "你的意见我们会认真考虑的"},
    { keys = "zhepianwenzhangdeguandianxinyingyongcijingquezuozhedewenbifeichangdute", expected = "这篇文章的观点新颖用词精确作者的文笔非常独特"},
    { keys = "zhegerenzaiwangluoshangyouhengaodeshengyubeiyuweixinyidaidechuangyejingying", expected = "这个人在网络上有很高的声誉被誉为新一代的创业精英"},
    { keys = "tadekeyanchengguozaiguojishangyinqileguangfandeguanzhu", expected = "他的科研成果在国际上引起了广泛的关注"},
    { keys = "zheweizuojiadezuopinfenggeduteyinqileguangfanguanzhu", expected = "这位作家的作品风格独特引起了广泛关注"},
    { keys = "zhejiagongsidechanpinzhiliangfeichangyoubaozheng", expected = "这家公司的产品质量非常有保证"},
    { keys = "tamengongsideyanfatuanduizaijishulingyuyouhengaodeshengyu", expected = "他们公司的研发团队在技术领域有很高的声誉"},
    { keys = "ruguoninengzaimingtianzhiqianwanchengzhefenbaogaowohuifeichangganji", expected = "如果你能在明天之前完成这份报告我会非常感激"},
    { keys = "jinguanjinglilexuduotiaozhantamenzuizhonghaishiqudelechenggong", expected = "尽管经历了许多挑战他们最终还是取得了成功"},
    { keys = "suirantianqibuhaodanwomenrengranjuedingchuquwanyitang", expected = "虽然天气不好但我们仍然决定出去玩一趟"},
    { keys = "tamengongsizuixintuichudezhinengshoujigongnengfeichangxianjinshichangfanxiangyefeichanghao", expected = "他们公司最新推出的智能手机功能非常先进市场反响也非常好"},
    { keys = "zhegedifangdelvyouziyuanfengfushiyigedujiadehaoquchu", expected = "这个地方的旅游资源丰富是一个度假的好去处"},
    { keys = "tamenganggangfabuleyikuanmingweixingyundexunixianshiyouxibeishouqidai", expected = "他们刚刚发布了一款名为幸运的虚拟现实游戏备受期待"},
    { keys = "ruguoninengtiqianwanchengzhexiangrenwuhuihenyoubangzhu", expected = "如果你能提前完成这项任务会很有帮助"},
    { keys = "jinguanyudaolekunnantamenyiranjianchixiaqu", expected = "尽管遇到了困难他们依然坚持下去"},
    { keys = "suiranxiayuledanshiwomenrengranjuedingchuquwanyihuier", expected = "虽然下雨了但是我们仍然决定出去玩一会儿"},
    { keys = "zhejiayiyuanyinjinlezuixindeyiliaoshebeitigaolezhiliaoxiaoguo", expected = "这家医院引进了最新的医疗设备提高了治疗效果"},
    { keys = "zhegechengshidejiaotongjianshezhengzaikuaisufazhan", expected = "这个城市的交通建设正在快速发展"},
    { keys = "tamendexinchanpinshejichuangxinxingshizu", expected = "他们的新产品设计创新性十足"},
    { keys = "shuruduanyudeshihou", expected = "输入短语的时候"},
    { keys = "tamenmeitiandouzaiyuanqupaobuduanlianshenti", expected = "他们每天都在远去跑步锻炼身体"},
    { keys = "tadefayanrangquanchangguanzhonggandongbuyi", expected = "他的发言让全场观众感动不已"},
    { keys = "zhejianshiqingdejiejuefanganyinggaizaiwenjianzhongzhaodao", expected = "这件事情的解决方案应该在文件中找到"},
    { keys = "tamenweilewanchengrenwuyizhizainuligongzuo", expected = "他们为了完成任务一直在努力工作"},
    { keys = "tadeyinyuezuopinyingdelequanguodehaoping", expected = "他的音乐作品赢得了全国的好评"},
    { keys = "tamenzuowanyijingyuedinglexiazhoudedehuiyi", expected = "他们昨晚已经约定了下周的的会议"},
    { keys = "woyaobazhegewentijiaogeininixiwangninenggoubangzhuwojiejue", expected = "我要把这个问题交给你你希望你能够帮助我解决"},
    { keys = "zhexiewentidedaanyijingfabule", expected = "这些问题的答案已经发布了"},
    { keys = "tamendefangzihenxiaodanshiweizhifeichanglixiang", expected = "他们的房子很小但是位置非常理想"},
    { keys = "zhexiangmudezhixingshijiandeyaojinyibutaolun", expected = "这项目的执行时间的要进一步讨论"},
    { keys = "tamendejihuazaiquanqiufanweineiyinqileguangfandeguanzhu", expected = "他们的计划在全球范围内引起了广泛的关注"},
    { keys = "gegeguojiadouyougegeguojiadeguoge", expected = "各个国家都有各个国家的国歌"},
    { keys = "tushuguandecangshu", expected = "图书馆的藏书"},
    { keys = "ceshiyixiachangjuzideshuruxiaoguo", expected = "测试一下长句子的输入效果"},
    { keys = "yingyuzhuanyehenchixiang", expected = "英语专业很吃香"},
    { keys = "jingguosangeyuedeshijian", expected = "经过三个月的时间"},
    { keys = "shuangpinshurufadajuzi", expected = "双拼输入法打句子"},
    { keys = "shuangpinshurufashurujuzi", expected = "双拼输入法输入句子"},
    { keys = "shuangpinshurufashuruchangjuzi", expected = "双拼输入法输入长句子"},
    { keys = "tamendexinchanpin", expected = "他们的新产品"},
    { keys = "shejichuangxinxingshizu", expected = "设计创新性十足"},
    { keys = "tamenzuotianyijingyuyuele", expected = "他们昨天已经预约了"},
    { keys = "mingtiandehuiyi", expected = "明天的回忆"},
    { keys = "woyaobazhegewentipaogeini", expected = "我要把这个问题抛给你"},
    { keys = "ninengbunengbangwojiedayixia", expected = "你能不能帮我解答一下"},
    { keys = "tamengongsizuixintuichudezhinengshouji", expected = "他们公司最新推出的智能手机"},
    { keys = "gongnengfeichangxianjin", expected = "功能非常先进"},
    { keys = "shichangfanxiangyefeichanghao", expected = "市场反响也非常好"},
    { keys = "chongmanxiwangdebashebidaodamudidigengnenggeirenlequ", expected = "充满希望的跋涉比到达目的地更能给人乐趣"},


--不敢在前不敢在后
--改样式快多了，我也就乐意写了

    -- 可以继续添加更多测试案例
}

local total_tests = 0
local correct_tests = 0
local incorrect_tests = 0

for _, case in ipairs(test_cases) do
    -- 模拟输入
    rimeac.simulate_keys(case.keys)
    
    -- 获取候选词和注释
    local cands, cmds = rimeac.get_candidates(), rimeac.get_comments()
    rimeac.select_candidate(1)
    -- rimeac.print_session()  -- 打印当前会话信息
    
    -- 自定义对比函数
    local function compare_with_status(actual, expected, message)
        if actual ~= expected then
            print(message .. " 实际值为 '" .. actual .. "', 期望值为 '" .. expected .. "'")
            return false
        end
        return true
    end
    
    -- 对比测试
    local result = compare_with_status(cands[1], case.expected, "第一个候选词不是")
    -- 这行会失败，所以会输出状态信息
    -- compare_with_status(cands[2], case.expected, "第二个候选词不是")
    total_tests = total_tests + 1
    if result then
        correct_tests = correct_tests + 1
    else
        incorrect_tests = incorrect_tests + 1
    end
    -- 这行会失败，所以会输出状态信息
    -- compare_with_status(cands[2], case.expected, "第二个候选词不是")
end

local correct_percentage = (correct_tests / total_tests) * 100
local incorrect_percentage = (incorrect_tests / total_tests) * 100

print("测试结果统计:")
print("正确/总数:", correct_tests .. "/" .. total_tests, string.format("(%.2f%%)", correct_percentage))
print("错误/总数:", incorrect_tests .. "/" .. total_tests, string.format("(%.2f%%)", incorrect_percentage))

--- select candidate on current session, >= 0
--- rimeac.select_candidate(1)
-- rimeac.print_session()

--- destroy all sessions
--- rimeac.destroy_sessions() no params
rimeac.destroy_sessions()

--- finalize rime
--- rimeac.finalize_rime() no params
rimeac.finalize_rime()

print("script ends!")
