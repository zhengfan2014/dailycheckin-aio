# -*- coding: utf-8 -*-
#改自https://github.com/Sitoi/dailycheckin/tree/main/bilibili
#版本2021-01-07
import json
import os

import requests
#配置信息
SCKEY = "server酱key"
Bili_cookie = '''{ "BILIBILI_COOKIE_LIST":[
        {
            "bilibili_cookie":"账号1cookie",
            "coin_num":0,
            "coin_type":1,
            "silver2coin":true
        },
        {
            "bilibili_cookie":"账号2cookie",
            "coin_num":0,
            "coin_type":1,
            "silver2coin":true
        }
    ]}'''

def ftqq(text,desp):
    if SCKEY != "":
        url = "https://sc.ftqq.com/" + SCKEY + ".send"
        r = requests.post(url,data={"text":text,"desp":desp})
        return "调用server酱成功" + r.text
    else:
        return "SCKEY未设置"
        

class BiliBiliCheckIn(object):
    # 待测试，需要大会员账号测试领取福利
    def __init__(self, bilibili_cookie_list):
        self.bilibili_cookie_list = bilibili_cookie_list

    @staticmethod
    def get_nav(session):
        url = "https://api.bilibili.com/x/web-interface/nav"
        ret = session.get(url=url).json()
        print(ret)
        uname = ret.get("data", {}).get("uname")
        uid = ret.get("data", {}).get("mid")
        is_login = ret.get("data", {}).get("isLogin")
        coin = ret.get("data", {}).get("money")
        vip_type = ret.get("data", {}).get("vipType")
        current_exp = ret.get("data", {}).get("level_info", {}).get("current_exp")
        return uname, uid, is_login, coin, vip_type, current_exp

    @staticmethod
    def reward(session) -> dict:
        """取B站经验信息"""
        url = "https://account.bilibili.com/home/reward"
        ret = session.get(url=url).json()
        return ret

    @staticmethod
    def live_sign(session) -> dict:
        """B站直播签到"""
        try:
            url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
            ret = session.get(url=url).json()
            if ret["code"] == 0:
                msg = f'签到成功，{ret["data"]["text"]}，特别信息:{ret["data"]["specialText"]}，本月已签到{ret["data"]["hadSignDays"]}天'
            elif ret["code"] == 1011040:
                msg = "今日已签到过,无法重复签到"
            else:
                msg = f'签到失败，信息为: {ret["message"]}'
        except Exception as e:
            msg = f"签到异常，原因为{str(e)}"
        return msg

    @staticmethod
    def manga_sign(session, platform="android") -> dict:
        """
        模拟B站漫画客户端签到
        """
        try:
            url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
            post_data = {"platform": platform}
            ret = session.post(url=url, data=post_data).json()
            if ret["code"] == 0:
                msg = "签到成功"
            elif ret["msg"] == "clockin clockin is duplicate":
                msg = "今天已经签到过了"
            else:
                msg = f'签到失败，信息为({ret["msg"]})'
        except Exception as e:
            msg = f"签到异常,原因为: {str(e)}"
        return msg

    @staticmethod
    def vip_privilege_receive(session, bili_jct, receive_type: int = 1) -> dict:
        """
        领取B站大会员权益
        receive_type int 权益类型，1为B币劵，2为优惠券
        """
        url = "https://api.bilibili.com/x/vip/privilege/receive"
        post_data = {"type": receive_type, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def vip_manga_reward(session) -> dict:
        """获取漫画大会员福利"""
        url = "https://manga.bilibili.com/twirp/user.v1.User/GetVipReward"
        ret = session.post(url=url, json={"reason_id": 1}).json()
        return ret

    @staticmethod
    def report_task(session, bili_jct, aid: int, cid: int, progres: int = 300) -> dict:
        """
        B站上报视频观看进度
        aid int 视频av号
        cid int 视频cid号
        progres int 观看秒数
        """
        url = "http://api.bilibili.com/x/v2/history/report"
        post_data = {"aid": aid, "cid": cid, "progres": progres, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def share_task(session, bili_jct, aid) -> dict:
        """
        分享指定av号视频
        aid int 视频av号
        """
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {"aid": aid, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def get_followings(
        session, uid: int, pn: int = 1, ps: int = 50, order: str = "desc", order_type: str = "attention"
    ) -> dict:
        """
        获取指定用户关注的up主
        uid int 账户uid，默认为本账户，非登录账户只能获取20个*5页
        pn int 页码，默认第一页
        ps int 每页数量，默认50
        order str 排序方式，默认desc
        order_type 排序类型，默认attention
        """
        params = {
            "vmid": uid,
            "pn": pn,
            "ps": ps,
            "order": order,
            "order_type": order_type,
        }
        url = f"https://api.bilibili.com/x/relation/followings"
        ret = session.get(url=url, params=params).json()
        return ret

    @staticmethod
    def space_arc_search(
        session, uid: int, pn: int = 1, ps: int = 100, tid: int = 0, order: str = "pubdate", keyword: str = ""
    ) -> dict:
        """
        获取指定up主空间视频投稿信息
        uid int 账户uid，默认为本账户
        pn int 页码，默认第一页
        ps int 每页数量，默认50
        tid int 分区 默认为0(所有分区)
        order str 排序方式，默认pubdate
        keyword str 关键字，默认为空
        """
        params = {
            "mid": uid,
            "pn": pn,
            "ps": ps,
            "tid": tid,
            "order": order,
            "keyword": keyword,
        }
        url = f"https://api.bilibili.com/x/space/arc/search"
        ret = session.get(url=url, params=params).json()
        data_list = [
            {"aid": one.get("aid"), "cid": 0, "title": one.get("title"), "owner": one.get("author")}
            for one in ret.get("data", {}).get("list", {}).get("vlist", [])
        ]
        return data_list

    @staticmethod
    def elec_pay(session, bili_jct, uid: int, num: int = 50) -> dict:
        """
        用B币给up主充电
        uid int up主uid
        num int 充电电池数量
        """
        url = "https://api.bilibili.com/x/ugcpay/trade/elec/pay/quick"
        post_data = {"elec_num": num, "up_mid": uid, "otype": "up", "oid": uid, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def coin_add(session, bili_jct, aid: int, num: int = 1, select_like: int = 1) -> dict:
        """
        给指定 av 号视频投币
        aid int 视频av号
        num int 投币数量
        select_like int 是否点赞
        """
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": bili_jct,
        }
        ret = session.post(url=url, data=post_data).json()

        return ret

    @staticmethod
    def live_status(session) -> dict:
        """B站直播获取金银瓜子状态"""
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        ret = session.get(url=url).json()
        data = ret.get("data")
        silver = data.get("silver", 0)
        gold = data.get("gold", 0)
        coin = data.get("coin", 0)
        msg = f" - 💿银瓜子数量: {silver}  \n - 📀金瓜子数量: {gold}  \n - 💰硬币数量: {coin}  "
        return msg

    @staticmethod
    def silver2coin(session, bili_jct) -> dict:
        """银瓜子兑换硬币"""
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        post_data = {"csrf_token": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def get_region(session, rid=1, num=6) -> dict:
        """
        获取 B站分区视频信息
        rid int 分区号
        num int 获取视频数量
        """
        url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
        ret = session.get(url=url).json()
        data_list = [
            {
                "aid": one.get("aid"),
                "cid": one.get("cid"),
                "title": one.get("title"),
                "owner": one.get("owner", {}).get("name"),
            }
            for one in ret.get("data", {}).get("archives", [])
        ]
        return data_list

    def main(self):
        msg_list = []
        for bilibili_info in self.bilibili_cookie_list:
            bilibili_cookie = {
                item.split("=")[0]: item.split("=")[1] for item in bilibili_info.get("bilibili_cookie").split("; ")
            }
            bili_jct = bilibili_cookie.get("bili_jct")
            coin_num = bilibili_info.get("coin_num", 0)
            coin_type = bilibili_info.get("coin_type", 1)
            silver2coin = bilibili_info.get("silver2coin", True)
            session = requests.session()
            requests.utils.add_dict_to_cookiejar(session.cookies, bilibili_cookie)
            session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108",
                    "Referer": "https://www.bilibili.com/",
                    "Connection": "keep-alive",
                }
            )
            success_count = 0
            uname, uid, is_login, coin, vip_type, current_exp = self.get_nav(session=session)
            # print(uname, uid, is_login, coin, vip_type, current_exp)
            if is_login:
                manhua_msg = self.manga_sign(session=session)
                print(manhua_msg)
                live_msg = self.live_sign(session=session)
                print(live_msg)
                aid_list = self.get_region(session=session)
                reward_ret = self.reward(session=session)
                print(reward_ret)
                coins_av_count = reward_ret.get("data", {}).get("coins_av") // 10
                coin_num = coin_num - coins_av_count
                coin_num = coin_num if coin_num < coin else coin
                print(coin_num)
                if coin_type == 1 and coin_num:
                    following_list = self.get_followings(session=session, uid=uid)
                    for following in following_list.get("data", {}).get("list"):
                        mid = following.get("mid")
                        if mid:
                            aid_list += self.space_arc_search(session=session, uid=mid)
                if coin_num > 0:
                    for aid in aid_list[::-1]:
                        # print(f'成功给{aid.get("title")}投一个币')
                        # coin_num -= 1
                        # success_count += 1
                        ret = self.coin_add(session=session, aid=aid.get("aid"), bili_jct=bili_jct)
                        if ret["code"] == 0:
                            coin_num -= 1
                            print(f'成功给{aid.get("title")}投一个币')
                            success_count += 1
                        elif ret["code"] == 34005:
                            print(f'投币{aid.get("title")}失败，原因为{ret["message"]}')
                            continue
                            # -104 硬币不够了 -111 csrf 失败 34005 投币达到上限
                        else:
                            print(f'投币{aid.get("title")}失败，原因为{ret["message"]}，跳过投币')
                            break
                        if coin_num <= 0:
                            break
                    coin_msg = f"今日成功投币{success_count + coins_av_count}/{bilibili_info.get('coin_num', 5)}个"
                    print(coin_msg)
                else:
                    coin_msg = f"今日成功投币{coins_av_count}/{bilibili_info.get('coin_num', 5)}个"
                    print(coin_msg)
                aid = aid_list[0].get("aid")
                cid = aid_list[0].get("cid")
                title = aid_list[0].get("title")
                report_ret = self.report_task(session=session, bili_jct=bili_jct, aid=aid, cid=cid)
                if report_ret.get("code") == 0:
                    report_msg = f"观看《{title}》300秒"
                else:
                    report_msg = f"任务失败"
                print(report_msg)
                share_ret = self.share_task(session=session, bili_jct=bili_jct, aid=aid)
                if share_ret.get("code") == 0:
                    share_msg = f"分享《{title}》成功"
                else:
                    share_msg = f"分享失败"
                print(share_msg)
                if silver2coin:
                    silver2coin_ret = self.silver2coin(session=session, bili_jct=bili_jct)
                    if silver2coin_ret["code"] == 0:
                        silver2coin_msg = f"成功将银瓜子兑换为1个硬币"
                    else:
                        silver2coin_msg = silver2coin_ret["msg"]
                    print(silver2coin_msg)
                else:
                    silver2coin_msg = f"未开启银瓜子兑换硬币功能"
                live_stats = self.live_status(session=session)
                uname, uid, is_login, new_coin, vip_type, new_current_exp = self.get_nav(session=session)
                print(uname, uid, is_login, new_coin, vip_type, new_current_exp)
                reward_ret = self.reward(session=session)
                login = reward_ret.get("data", {}).get("login")
                watch_av = reward_ret.get("data", {}).get("watch_av")
                coins_av = reward_ret.get("data", {}).get("coins_av", 0)
                share_av = reward_ret.get("data", {}).get("share_av")
                today_exp = len([one for one in [login, watch_av, share_av] if one]) * 5
                today_exp += coins_av
                
                progress = ""
                if mylevel(new_current_exp)[1] == 0:
                    update_data= "通过答题测试才能升级哦"
                elif mylevel(new_current_exp)[1] == 999999999:
                    update_data= "已经满级了哦"
                else:
                    update_data = str(mylevel(new_current_exp)[0] + 1) + "还需: " + str((mylevel(new_current_exp)[1] - new_current_exp) // (today_exp if today_exp else 1)) + "天"
                    progress = expprogress(new_current_exp,mylevel(new_current_exp)[1])
                    per = expprogress(new_current_exp,mylevel(new_current_exp)[1],mode="per")
                msg = (
                    f"## 【Bilibili签到】\n"
                    f"### ✏签到信息\n"
                    f"👴帐号信息: {uname}  \n"
                    f"📕漫画签到: {manhua_msg}  \n"
                    f"🎦直播签到: {live_msg}  \n"
                    f"📌登陆任务: 今日已登陆  \n"
                    f"👀观看视频: {report_msg}  \n"
                    f"👏分享任务: {share_msg}  \n"
                    f"💰投币任务: {coin_msg}  \n"
                    f"🎫银瓜子兑换硬币: {silver2coin_msg}  \n"
                    f"\n ----- \n"
                    f"### 😃经验信息\n"
                    f"🏆今日获得经验: {today_exp}  \n"
                    f"📈当前经验: {new_current_exp}  \n"
                    f"{progress} {per}%  \n"
                    f"⌚按当前速度升级Lv.{update_data}  \n"
                    f"\n ----- \n"
                    f"### 💵资产信息\n"
                    f"{live_stats}"
                )
                print(msg)
                
                print(ftqq("Bilibili签到",msg))
                msg_list.append(msg)
        return msg_list

def mylevel(exp):
    exp = int(exp)
    if exp > 0 and exp < 200:
        level = 1
        maxexp = 200
    elif exp >= 200 and exp < 1500:
        level = 2
        maxexp = 1500
    elif exp >= 1500 and exp < 4500:
        level = 3
        maxexp = 4500
    elif exp >= 4500 and exp < 10800:
        level = 4
        maxexp = 10800
    elif exp >= 10800 and exp < 28800:
        level = 5
        maxexp = 28800
    elif exp >= 28800:
        level = 6
        maxexp = 999999999
    else:
        level = 0
        maxexp = 0
    return [level,maxexp]
def expprogress(nowexp,maxexp,mode="progress"):
    black = "█"
    white = "░"
    num = round(((float(nowexp) / float(maxexp))*100)/5)
    progress = black*num + white*((20-num)*2)
    if mode == "progress":
        return progress
    else:
        return num*5
if __name__ == "__main__":
    datas = json.loads(Bili_cookie)
    _bilibili_cookie_list = datas.get("BILIBILI_COOKIE_LIST", [])
    BiliBiliCheckIn(bilibili_cookie_list=_bilibili_cookie_list).main()
