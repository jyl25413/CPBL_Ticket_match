from app import app, db
from models import User, Listing, WantToBuy, Application, Order, Rating, Notification

def seed_database():
    with app.app_context():
        # Clear existing data for fresh seed
        db.drop_all()
        db.create_all()
        print("Creating fresh database tables...")

        # 1. Dragons (味全龍) Users
        dragons_users = [
            ("張永昕", "chang_ys@example.com", "https://facebook.com/chang.ys", 5.0, 0),
            ("Yuri_Liu", "yuri_l@example.com", "https://facebook.com/yuri.liu", 4.9, 0),
            ("施亞彤", "shi_yt@example.com", "https://facebook.com/shi.yt", 5.0, 0),
            ("Chun_Ting_Li", "li_ct@example.com", "https://facebook.com/chun.ting.li", 4.8, 0),
            ("Eason_Liu", "eason_l@example.com", "https://facebook.com/eason.liu", 5.0, 0),
            ("陳亭妃", "chen_tf@example.com", "https://facebook.com/chen.tf", 4.7, 1),
            ("品卉", "pin_hui@example.com", "https://facebook.com/pinhui", 5.0, 0),
            ("洪睿言", "hong_ry@example.com", "https://facebook.com/hong.ry", 4.9, 0),
            ("黃元慶", "huang_yc@example.com", "https://facebook.com/huang.yc", 5.0, 0),
            ("Chun_Lin_Lai", "lai_cl@example.com", "https://facebook.com/chunlin.lai", 4.8, 0),
            ("劉暖", "liu_nuan@example.com", "https://facebook.com/liu.nuan", 5.0, 0),
            ("陳志龍", "chen_cl@example.com", "https://facebook.com/chen.cl", 5.0, 0),
            ("盧奐廷", "lu_ht@example.com", "https://facebook.com/lu.ht", 4.9, 0),
            ("劉俊威", "liu_cw@example.com", "https://facebook.com/liu.cw", 5.0, 0),
            ("林政忠", "lin_jc@example.com", "https://facebook.com/lin.jc", 4.6, 0),
            ("Jeffery_Chen", "jeffery_c@example.com", "https://facebook.com/jeffery.chen", 5.0, 0),
            ("Sky_Hsu", "sky_hsu@example.com", "https://facebook.com/sky.hsu", 4.9, 0),
            ("范雯綺", "fan_wc@example.com", "https://facebook.com/fan.wc", 5.0, 0),
            ("高立軒", "kao_lh@example.com", "https://facebook.com/kao.lh", 4.8, 0),
            ("David_Chang", "david_c@example.com", "https://facebook.com/david.chang", 5.0, 0),
            ("賴柏綸", "lai_pl@example.com", "https://facebook.com/lai.pl", 5.0, 0),
            ("陳志豪", "chen_ch@example.com", "https://facebook.com/chen.ch", 4.9, 0),
        ]

        # 2. Guardians (富邦悍將) Users
        guardians_users = [
            ("王柔蒨", "wang_rc@example.com", "https://facebook.com/wang.rc", 5.0, 0),
            ("劉明瀚", "liu_mh@example.com", "https://facebook.com/liu.mh", 4.9, 0),
            ("Renhau_Lin", "renhau_l@example.com", "https://facebook.com/renhau.lin", 5.0, 0),
            ("Abner_Hong", "abner_h@example.com", "https://facebook.com/abner.hong", 4.8, 0),
            ("林儀昕", "lin_ys@example.com", "https://facebook.com/lin.ys", 5.0, 0),
            ("Ht_Ruf", "ht_ruf@example.com", "https://facebook.com/ht.ruf", 4.7, 0),
            ("林承佑", "lin_cy@example.com", "https://facebook.com/lin.cy", 5.0, 0),
            ("Bruce_Huang", "bruce_h@example.com", "https://facebook.com/bruce.h", 4.9, 0),
            ("周祖安", "chou_ca@example.com", "https://facebook.com/chou.ca", 5.0, 0),
            ("陳建閔", "chen_cm@example.com", "https://facebook.com/chen.cm", 4.8, 0),
            ("宋才聞", "song_cw@example.com", "https://facebook.com/song.cw", 5.0, 0),
            ("歐約昇", "ou_ys@example.com", "https://facebook.com/ou.ys", 5.0, 0),
            ("詹姆士", "james_fubon@example.com", "https://facebook.com/james.fubon", 4.9, 0),
            ("CU_Hao", "cu_hao@example.com", "https://facebook.com/cu.hao", 5.0, 0),
            ("曾俊賢", "tseng_ch@example.com", "https://facebook.com/tseng.ch", 4.8, 0),
            ("曹文馨", "tsao_wh@example.com", "https://facebook.com/tsao.wh", 5.0, 0),
            ("邱大安", "chiu_ta@example.com", "https://facebook.com/chiu.ta", 5.0, 0),
            ("王宣文", "wang_sw@example.com", "https://facebook.com/wang.sw", 4.9, 0),
            ("Amber_Lien", "amber_l@example.com", "https://facebook.com/amber.lien", 5.0, 0),
            ("鄧宇翔", "teng_ys@example.com", "https://facebook.com/teng.ys", 4.7, 0),
            ("Funny_Liu", "funny_l@example.com", "https://facebook.com/funny.liu", 5.0, 0),
            ("陳柏年", "chen_pn@example.com", "https://facebook.com/chen.pn", 4.9, 0),
            ("張博政", "chang_pc@example.com", "https://facebook.com/chang.pc", 5.0, 0),
            ("謝旻達", "hsieh_mt@example.com", "https://facebook.com/hsieh.mt", 4.8, 0),
        ]

        # 3. TSG Hawks (台鋼雄鷹) Users
        hawks_users = [
            ("台鋼鷹皇專賣", "tsg_hawks@example.com", "https://facebook.com/tsg.hawks.tickets", 5.0, 0),
            ("鷹雄應援團長", "tsg_hero@example.com", "https://facebook.com/tsg.hero", 4.9, 0),
        ]

        user_objects = {}
        all_users = dragons_users + guardians_users + hawks_users
        for username, email, social, rating, default_cnt in all_users:
            u = User(
                username=username,
                email=email,
                social_link=social,
                rating_avg=rating,
                default_count=default_cnt
            )
            u.set_password("password123")
            db.session.add(u)
            user_objects[username] = u

        db.session.commit()
        print(f"Added {len(user_objects)} users (Dragons + Guardians + TSG Hawks)!")

        # 4. Dragons Listings
        dragons_listings = [
            ("張永昕", "ticket", "味全龍", "台北大巨蛋", "8/19 本後 112 區 6 排 (實際第 2 排)", "全票", "中職官方APP轉贈", 1200, 1200, 1),
            ("Yuri_Liu", "ticket", "味全龍", "台北大巨蛋", "8/15 115 區 24 排 (靠走道)", "全票", "中職官方APP轉贈", 2250, 2250, 1),
            ("Yuri_Liu", "ticket", "味全龍", "台北大巨蛋", "8/15 216 區 2 排連號 (靠走道)", "全票", "中職官方APP轉贈", 1950, 1950, 2),
            ("Chun_Ting_Li", "ticket", "味全龍", "台北大巨蛋", "8/15 117 區 25 排兩張連號", "全票", "中職官方APP轉贈", 2200, 2200, 2),
            ("Eason_Liu", "ticket", "味全龍", "台北大巨蛋", "8/14 106 區 14 排兩連號", "全票", "中職官方APP轉贈", 1600, 1600, 2),
            ("品卉", "ticket", "味全龍", "台北大巨蛋", "8/14 B1 內野 111 區 24 排 1,2 號 (走道位)", "全票", "中職官方APP轉贈", 1200, 1200, 2),
            ("洪睿言", "ticket", "味全龍", "台北大巨蛋", "8/14 117 區 20 排連號 (同場歡呼龍迷佳)", "全票", "中職官方APP轉贈", 1100, 1100, 2),
            ("黃元慶", "ticket", "味全龍", "台北大巨蛋", "8/20 108 區 16 排 6-7 號二連號", "全票", "中職官方APP轉贈", 1250, 1250, 2),
            ("Chun_Lin_Lai", "ticket", "味全龍", "台北大巨蛋", "8/19 110 區 23 排 走道位三連號 (靠 109 側)", "全票", "中職官方APP轉贈", 1300, 1300, 3),
            ("劉暖", "ticket", "味全龍", "台北大巨蛋", "8/14 本後 113 區 8 排 尊榮單張", "全票", "中職官方APP轉贈", 1300, 1300, 1),
            ("盧奐廷", "ticket", "味全龍", "台北大巨蛋", "8/16 B1 內野 109 區 24 排 2 號", "全票", "中職官方APP轉贈", 1350, 1350, 1),
            ("劉俊威", "ticket", "味全龍", "台北大巨蛋", "8/14 117 區 18 排熱區", "全票", "中職官方APP轉贈", 1350, 1350, 1),
            ("林政忠", "ticket", "味全龍", "台北大巨蛋", "8/16 117 區 13 排大號", "全票", "中職官方APP轉贈", 1530, 1530, 1),
            ("Jeffery_Chen", "ticket", "味全龍", "台北大巨蛋", "8/20 鷹祭 B1 123 區 (折價回饋龍迷)", "全票", "中職官方APP轉贈", 700, 450, 1),
            ("Sky_Hsu", "ticket", "味全龍", "台北大巨蛋", "8/14 108 區 15-17, 15-18 兩張連號走道位", "全票", "中職官方APP轉贈", 1350, 1350, 2),
            ("范雯綺", "ticket", "味全龍", "台北大巨蛋", "8/15 B1 108 區 21 排", "全票", "中職官方APP轉贈", 2250, 2250, 1),
            ("高立軒", "ticket", "味全龍", "台北大巨蛋", "8/15 217 區 7 排", "全票", "中職官方APP轉贈", 1800, 1800, 1),
            ("賴柏綸", "merch", "味全龍", "天母棒球場", "8/29 天母熱區票券與龍隊優惠入場禮", "季票/會員票", "現場面交", 800, 800, 2),
            ("陳志豪", "ticket", "味全龍", "台北大巨蛋", "8/20 L2 209 區 2 排 3-5 三連號 (週間票優惠)", "全票", "超商取票序號", 500, 350, 3),
        ]

        # 5. Guardians Listings
        guardians_listings = [
            ("王柔蒨", "ticket", "富邦悍將", "新莊棒球場", "8/8 B7 區 7 排 10 號 / 9 排 10 號", "全票", "中職官方APP轉贈", 700, 700, 2),
            ("劉明瀚", "ticket", "富邦悍將", "新莊棒球場", "8/8 A1 區 8 排 12 號原價熱區", "全票", "中職官方APP轉贈", 700, 700, 1),
            ("Renhau_Lin", "ticket", "富邦悍將", "新莊棒球場", "8/8 A7 熱區 8 排 二連號 (11,12 號)", "全票", "中職官方APP轉贈", 700, 700, 2),
            ("Renhau_Lin", "ticket", "富邦悍將", "新莊棒球場", "8/9 B7 熱區 13 排 二連號 (5,6 號)", "全票", "中職官方APP轉贈", 700, 700, 2),
            ("Abner_Hong", "ticket", "富邦悍將", "新莊棒球場", "8/7 A3 區 13 排 9 號 (便宜出清)", "全票", "中職官方APP轉贈", 450, 300, 1),
            ("林儀昕", "ticket", "富邦悍將", "新莊棒球場", "8/7 B8 區 4 排 1-2 號二連號", "全票", "中職官方APP轉贈", 450, 200, 2),
            ("Ht_Ruf", "ticket", "富邦悍將", "新莊棒球場", "8/9 A2 區 14 排 5 號 (雨天可依規定處理)", "全票", "中職官方APP轉贈", 700, 700, 1),
            ("林承佑", "ticket", "富邦悍將", "新莊棒球場", "8/7 B6 區 6 排 2 號熱力區", "全票", "中職官方APP轉贈", 650, 650, 1),
            ("Bruce_Huang", "ticket", "富邦悍將", "新莊棒球場", "8/8 A1 區 9 排原價票", "全票", "中職官方APP轉贈", 700, 700, 1),
            ("周祖安", "ticket", "富邦悍將", "新莊棒球場", "8/9 B3 區 17 排二連號 (可小刀優惠)", "全票", "中職官方APP轉贈", 700, 650, 2),
            ("陳建閔", "ticket", "富邦悍將", "新莊棒球場", "8/9 B4 區 11 排小號 (位子佳讓售)", "全票", "中職官方APP轉贈", 700, 600, 1),
            ("歐約昇", "ticket", "富邦悍將", "新莊棒球場", "8/7 A3 區 13 排 (颱風降價讓票)", "全票", "中職官方APP轉贈", 450, 350, 1),
            ("詹姆士", "ticket", "富邦悍將", "新莊棒球場", "8/7 熱力區 B4 區 6 排 1 張", "全票", "中職官方APP轉贈", 450, 450, 1),
            ("CU_Hao", "ticket", "富邦悍將", "新莊棒球場", "8/7 A5 區 8 排 / A6 區 12 排大號", "全票", "中職官方APP轉贈", 450, 350, 2),
            ("曾俊賢", "ticket", "富邦悍將", "新莊棒球場", "8/7 A1 區 14 排 (實體票今日新莊城堡面交)", "全票", "現場面交", 450, 450, 1),
            ("曹文馨", "ticket", "富邦悍將", "新莊棒球場", "8/9(日) A7 區 10 排 2 連號原價", "全票", "中職官方APP轉贈", 700, 700, 2),
            ("邱大安", "ticket", "富邦悍將", "新莊棒球場", "8/8 A3 熱區 14 排 四連號 (可兩張一組)", "全票", "中職官方APP轉贈", 700, 700, 4),
            ("王宣文", "ticket", "富邦悍將", "新莊棒球場", "8/7 A6 區 10 排 連號三張 (全收優先)", "全票", "中職官方APP轉贈", 450, 450, 3),
            ("Amber_Lien", "ticket", "富邦悍將", "新莊棒球場", "8/7 B3 區 13 排走道位", "全票", "中職官方APP轉贈", 450, 450, 1),
            ("鄧宇翔", "ticket", "富邦悍將", "新莊棒球場", "8/8 B2 區 14 排 1 張", "全票", "中職官方APP轉贈", 700, 700, 1),
            ("Funny_Liu", "ticket", "富邦悍將", "新莊棒球場", "8/7 A8 區 4 排 聯名卡特惠票", "全票", "中職官方APP轉贈", 450, 200, 1),
            ("陳柏年", "ticket", "富邦悍將", "新莊棒球場", "8/7 外野熱區 G9 區 7 排 1 號 (走道位)", "全票", "中職官方APP轉贈", 350, 350, 1),
            ("張博政", "ticket", "富邦悍將", "新莊棒球場", "8/8 B7 區 7 排 4-5 號降價售", "全票", "中職官方APP轉贈", 700, 550, 2),
            ("謝旻達", "ticket", "富邦悍將", "新莊棒球場", "8/7 B6 區 13 排 (小號近走道)", "全票", "中職官方APP轉贈", 450, 300, 1),
            ("謝旻達", "ticket", "富邦悍將", "新莊棒球場", "8/8 A2 區 9 排熱區", "全票", "中職官方APP轉贈", 700, 600, 1),
        ]

        # 6. TSG Hawks (台鋼雄鷹) Listings from the latest FB Post
        hawks_listings = [
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/7 鷹皇位 I3, R3 / I5-二連", "全票", "中職官方APP轉贈", 1000, 1000, 2),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/8 鷹皇位 R3 / I5 四連號", "全票", "中職官方APP轉贈", 1000, 1000, 4),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/8 鷹皇位 I6 單張 / I8 單張 / P8 二連號", "全票", "中職官方APP轉贈", 1000, 1000, 2),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/9 鷹皇位 R3, R5 四連號 / P5 三連號 / I7 單張", "全票", "中職官方APP轉贈", 1000, 1000, 4),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/11 鷹皇位 I3, R3 尊榮視野", "全票", "中職官方APP轉贈", 1000, 1000, 1),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/12 鷹皇位 I3, R3", "全票", "中職官方APP轉贈", 1000, 1000, 1),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/21 鷹皇位 R3", "全票", "中職官方APP轉贈", 1000, 1000, 1),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/22 鷹皇位 R3/I3 / I5 二連+單張 (不拆賣)", "全票", "中職官方APP轉贈", 1000, 1000, 3),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/22 鷹皇位 P6 二連 / R7 二連 / I7 二連", "全票", "中職官方APP轉贈", 1000, 1000, 2),
            ("台鋼鷹皇專賣", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/23 鷹皇位 R3/I3 P5 二連 / P6 二連 / R8 四連號", "全票", "中職官方APP轉贈", 1000, 1000, 4),
            ("鷹雄應援團長", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "9/1 鷹皇位 R3/I3", "全票", "中職官方APP轉贈", 1000, 1000, 1),
            ("鷹雄應援團長", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "9/2 鷹皇位 R3/I3", "全票", "中職官方APP轉贈", 1000, 1000, 1),
            ("鷹雄應援團長", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "9/15 鷹皇位 R3/I3", "全票", "中職官方APP轉贈", 1000, 1000, 1),
        ]

        created_listings = []
        all_listings = dragons_listings + guardians_listings + hawks_listings
        for seller_name, cat, team, stadium, zone, ttype, delivery, orig_p, price, qty in all_listings:
            seller = user_objects.get(seller_name)
            if seller:
                lst = Listing(
                    seller_id=seller.id,
                    category=cat,
                    team=team,
                    stadium=stadium,
                    zone=zone,
                    ticket_type=ttype,
                    delivery_method=delivery,
                    original_price=orig_p,
                    price=price,
                    quantity=qty,
                    status='active'
                )
                db.session.add(lst)
                created_listings.append(lst)

        db.session.commit()
        print(f"Added {len(created_listings)} listings (Dragons + Guardians + TSG Hawks)!")

        # 7. WTB Posts (徵票)
        wtb_data = [
            ("施亞彤", "ticket", "味全龍", "台北大巨蛋", "8/16 116-118區或108-110區 二連號，求前排熱區！", 2500, 2),
            ("陳亭妃", "ticket", "味全龍", "天母棒球場", "8/29 A7-A8 B1-B4 熱區一張", 1000, 1),
            ("黃元慶", "ticket", "味全龍", "台北大巨蛋", "8/19 107或119區前14排單張", 1500, 1),
            ("David_Chang", "ticket", "味全龍", "台北大巨蛋", "【急徵】8/14 109或117區 15排前連號2張", 2000, 2),
            ("宋才聞", "ticket", "富邦悍將", "新莊棒球場", "8/7 內野四連號求票", 500, 4),
            ("鷹雄應援團長", "ticket", "台鋼雄鷹", "高雄澄清湖棒球場", "8/23 徵求 P6 區二連號熱區門票", 1000, 2),
        ]

        for buyer_name, cat, team, stadium, zone, max_p, qty in wtb_data:
            buyer = user_objects.get(buyer_name)
            if buyer:
                wtb = WantToBuy(
                    buyer_id=buyer.id,
                    category=cat,
                    team=team,
                    stadium=stadium,
                    zone=zone,
                    max_price=max_p,
                    quantity=qty,
                    status='active'
                )
                db.session.add(wtb)

        db.session.commit()
        print("Added WTB posts!")

        # 8. Applications & Demo Escrow Orders
        buyer1 = user_objects["施亞彤"]
        buyer2 = user_objects["David_Chang"]
        seller_zhang = user_objects["張永昕"]
        listing_zhang = created_listings[0]

        app1 = Application(listing_id=listing_zhang.id, buyer_id=buyer1.id, status='pending')
        app2 = Application(listing_id=listing_zhang.id, buyer_id=buyer2.id, status='pending')
        db.session.add(app1)
        db.session.add(app2)

        # Create an in-progress Mock Escrow Order for illustration
        listing_jeff = created_listings[13]
        buyer_david = user_objects["David_Chang"]
        order_example = Order(
            listing_id=listing_jeff.id,
            buyer_id=buyer_david.id,
            seller_id=listing_jeff.seller_id,
            status='paid',
            note='買家 APP 轉贈手機：0987-654-321'
        )
        listing_jeff.status = 'pending'
        db.session.add(order_example)

        db.session.commit()
        print("Created demo application and in-progress order!")
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
