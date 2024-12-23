import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


""" ゲーム内エンティティに関するクラス群 - Bird, Enemy, Boss, Coin """

class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
            if key_lst[pg.K_s]:  # sキーを押しているときは速さ1.5倍
                self.speed = 15
            else:
                self.speed = 10
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vx, self.vy = 0, +6
        self.bound = random.randint(50, HEIGHT//2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 200)  # 爆弾投下インターバル
    # 停止後移動
        for i in range (100) :
            self.rl = -1 ** i  # 左右
        self.ud = 2  # 振動幅
        self.rl_speed = random.randint(1,3)  # 左右スピード
        self.ud_off = 0  # 初期値

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"

        if self.state == "stop":
            self.rect.x += self.rl * self.rl_speed
            self.ud_off = self.ud * math.sin(pg.time.get_ticks() * 0.002)
            self.rect.y += self.ud_off
        # 跳ね返り 
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.rl *= -1

        self.rect.move_ip(self.vx, self.vy)


class Boss():
    """
    ボスキャラに関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/alien1.png"), 0, 3.0)
        self.rect = self.image.get_rect()  # 座標取得
        self.rect.center = WIDTH//2, 0
        self.vx, self.vy = 0, +1  # 加速度
        self.bound = HEIGHT//3
        self.state = "none"  # 最初は描画しない
    
    def update(self, screen:pg.Surface):
        """
        ボスを速度ベクトルself.vx,vyに基づき移動させる
        登場時、指定位置まで下降したら一旦停止
        停止後、左右端まで移動したら，self.vxの正負を逆転する
        引数 screen：画面Surface
        """
        if self.state == "none":  # noneステータスで呼び出されたら
            self.state = "down"  # 下降を始めて登場させる
        if self.state == "down":  # 下降中
            if self.rect.centery > self.bound:  # 指定位置に達したら
                self.vy = 0  # 移動をやめて
                self.state = "stop"  # いったん停止モードに
        if self.state == "stop":  # 停止中なら
            self.vx = 3  # x座標方向に加速度を与える
            self.state = "move"  # ステータスを変更
        if self.state == "move":  # move中なら
            if check_bound(self.rect) != (True, True):
                self.vx *= -1  # 画面端に達したとき反転
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.image, self.rect)


class Coin(pg.sprite.Sprite):
    """
    コインの生成に関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/coin.png"), 0, 0.05) #コインの画像Surfaceを生成し大きさを調整
        self.rect = self.image.get_rect() # 画像範囲を取得
        r_x = random.randint(0,WIDTH) # x座標
        r_y = random.randint(0,HEIGHT) # y座標
        self.rect.center = (r_x, r_y) #コインの中心座標
    
    def update(self, screen: pg.Surface):
        """
        コインを描画する
        """
        screen.blit(self.image, self.rect)
        
    
""" 攻撃に関するクラス群 - Beam, NeoBeam, Bomb, Explosion """

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle0=0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        引数 angle0：弾幕用ビームの回転角度の加算量
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0  # 角度を加算
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class NeoBeam():
    """
    分散したビームを放つ弾幕攻撃を生成するクラス
    """
    def __init__(self, bird: Bird, num: int|float):
        """
        弾幕用のBeamに関する設定
        引数 bird：ビームを放つこうかとん
        引数 num：ビームの数
        """
        self.bird = bird
        self.num = num
    
    def gen_beams(self):
        bm_lst = []  # Beamインスタンスを格納するリスト
        step = 100 // (self.num-1)  # ステップ数を計算
        for r in range(-50, +51, step):
            bm_lst.append(Beam(self.bird, r))  # Beamインスタンスを生成し、リストに追加
        return bm_lst


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6
    
    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
    

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """

    #scaleを設定し、こうかとんが攻撃を受けたときにだけ小さく表示する
    def __init__(self, obj: "Bomb|Enemy", life: int , scale = 1.0):  
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [pg.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))),pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


""" 特殊アビリティに関するクラス群 Shield, Gravity, Emp """

class Shield(pg.sprite.Sprite):
    """
    防御壁を出現させ、着弾を防ぐ
    """
    def __init__(self, bird: Bird, life: int):
        super().__init__()
        self.bird = bird
        self.life = life
        self.height = self.bird.image.get_height() # こうかとんの高さ
        self.width = self.bird.image.get_width() # こうかとんの幅
        vx, vy = bird.dire # こうかとんの向きを取得
        x = self.bird.rect.centerx+self.width*vx # shieldのx座標
        y = self.bird.rect.centery+self.height*vy # shieldのy座標
        self.image = pg.Surface((20, self.height*2))
        pg.draw.rect(self.image, (0, 91, 172), (0, 0, 20, self.height*2)) #青い矩形を描画
        angle = math.degrees(math.atan2(-vy, vx)) #角度を求める
        self.image = pg.transform.rotozoom(self.image, angle, 1.0) #回転
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.image.set_colorkey((0, 0, 0))
    
    def update(self):
        """
        lifeが0未満になったら防御壁を削除
        """
        self.life -= 1
        if self.life < 0:
            self.kill()


class Gravity(pg.sprite.Sprite):
    """
    追加機能2：重力場に関するクラス
    """
    def __init__(self, screen, life = 400):
        """
        重力場のSurfaceと対応するRectを生成する
        """
        super().__init__()
        self.life = life
        self.image = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(self.image, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()

    def update(self):
        """
        lifeを1減算し、0未満になったらkillする
        """
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Emp:
    """
    追加機能3：電磁パレス(EMP)に関するクラス
    """
    def __init__(self, emys:pg.sprite.Sprite, bombs:pg.sprite.Sprite, screen):
        self.go_img = pg.Surface((WIDTH,HEIGHT)) #　四角
        pg.draw.rect(self.go_img, (255, 255, 0), pg.Rect(0,0,WIDTH,HEIGHT))
        self.go_rct = self.go_img.get_rect()  # 爆弾rectの抽出
        self.go_img.set_alpha(100)  # 0から255
        screen.blit(self.go_img,self.go_rct)
        pg.display.update()
        time.sleep(0.05)


""" 数値に関するクラス Score, Combo, Time """

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        if self.value < 0:
            self.value = 0
        screen.blit(self.image, self.rect)


class Combo:
    """
    コンボに関するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 215, 0)
        self.value = 0
        self.image = self.font.render(f"{self.value}combo", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-100
        self.cnt = 0  # inc_combが呼び出されるたびに加算
        self.lst = [] # 撃墜時刻を保存しておくリスト
    
    def inc_comb(self, attime:time)->bool:
        """
        コンボ加算の対象かどうかを判別する関数
        引数：撃墜した時刻(時間型)
        戻り値：bool値
        """
        comb_time = 0  # 撃墜時間計算用の変数を０で初期化
        self.cnt += 1
        self.lst.append(attime)  # 撃墜時刻をリストに追加
        if self.cnt != 1:  # 初回呼び出しでなければ
            comb_time = abs(self.lst[-2] - self.lst[-1])  # 前回の撃墜からの経過時間を計算
        if comb_time < 2.0:  # 2秒以内のキルなら
            return True
        else: return False

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"{self.value}combo", 0, self.color)
        screen.blit(self.image, self.rect)
        if self.value < 0:
            self.value = 0
        if len(self.lst) > 10:  # キル履歴が10件以上あったら
            del self.lst[:8]  # 末尾２つを残して削除する


class Times():
    """
    時間経過に応じてゲーム全体をコントロールする関数
    """
    def __init__(self):
        self.timefont = pg.font.Font(None, 50)
        self.timecolor = (255,255,255)
        self.starttime = pg.time.get_ticks()
    
    def update(self, screen: pg.Surface):
        start_time = 0
        time_ms = pg .time.get_ticks() - start_time # ゲームの開始からの経過時間をミリ秒単位で取得します。
        time_byou = time_ms // 1000
        time_min ,seconds = divmod(time_byou,60)
        time_str = f"{time_min:02}:{seconds:02}"

        self.timeimage = self.timefont.render(time_str, True, self.timecolor)
        self.timerect = self.timeimage.get_rect()
        self.timerect.topright = (WIDTH -980, 20)
        screen.blit(self.timeimage, self.timerect)


""" 以下、main関数 """

def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    #背景画像のロード
    bg_img1 = pg.image.load(f"fig/bg/bg1.jpg")
    bg_img2 = pg.image.load(f"fig/bg/bg2.jpg")
    bg_img3 = pg.image.load(f"fig/bg/bg3.jpg")
    bg_img4 = pg.image.load(f"fig/bg/bg4.jpg")
    bg_img5 = pg.image.load(f"fig/bg/bg5.jpg")
    #背景画像の大きさの変更
    bg_img1 = pg.transform.scale(bg_img1, (WIDTH, HEIGHT))
    bg_img2 = pg.transform.scale(bg_img2, (WIDTH, HEIGHT))
    bg_img3 = pg.transform.scale(bg_img3, (WIDTH, HEIGHT))
    bg_img4 = pg.transform.scale(bg_img4, (WIDTH, HEIGHT))
    bg_img5 = pg.transform.scale(bg_img5, (WIDTH, HEIGHT))
    bg_img_list = [bg_img1, bg_img2, bg_img3, bg_img4, bg_img5]  # 背景画像のリストの作成
    bg_image = random.choice(bg_img_list)  # 背景画像をランダムで選ぶ
    
    # オブジェクト生成：スコア、コンボ、時間表示
    score = Score()
    combo = Combo()
    timed = Times()

    # こうかとんオブジェクトの生成
    bird = Bird(3, (900, 400))

    # 各Groupオブジェクトの生成
    bombs = pg.sprite.Group()  # 爆弾
    beams = pg.sprite.Group()  # ビーム
    exps = pg.sprite.Group()  # 爆発エフェクト
    emys = pg.sprite.Group()  # 敵機
    coins = pg.sprite.Group()  # コイン
    gravity_group = pg.sprite.Group()  # 重力場
    emp = pg.sprite.Group()  # パルス
    shield = pg.sprite.Group()  # シールド
    # boss = pg.sprite.Group()  # ボス
    boss_attack = 10  # ボスへの攻撃回数
    
    # tick
    tmr = 0
    clock = pg.time.Clock()

    # こうかとんのHP
    life = 10  # 残機10に設定
    life_icon =  pg.transform.rotozoom(pg.image.load(f"fig/0.png"), 0, 0.7) 
    pg.init
    font_hp = pg.font.Font(None, 36) # HP
    font_go = pg.font.Font(None, 100) # GameOver

    # ゲーム
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():  # ボタンが押されて起こるfor文
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if key_lst[pg.K_z]:  # Zキーも押していたら
                    many_beams = NeoBeam(bird, num=5)
                    beams.add(many_beams.gen_beams())
                else:
                    beams.add(Beam(bird))
            
            # 重力場攻撃
            if key_lst[pg.K_RETURN]:  # RETURNを押したら
                if combo.value >= 20:  # comboが20以上なら
                    gravity = Gravity(screen)  # Gravityクラスを呼び出す
                    gravity_group.add(gravity)  # インスタンスをGroupオブジェクトに追加
                    combo.value -= 20  # 重力場呼び出すとき使ったスコア文を引く
            
            # パルス攻撃
            if event.type == pg.KEYDOWN and event.key == pg.K_e and combo.value >= 20:  # comboが20以上なら
                Emp(emys, bombs, screen)
                combo.value -= 20
                for emy in emys:
                    emy.interval = float('inf')  # 敵機が爆弾を投下できなくする
                    emy.image = pg.transform.laplacian(emy.image)
                for bomb in bombs:
                    bomb.speed /= 2  # 動き鈍く
                    bomb.state = "inactive"  # 爆弾の状態を無効

            # シールド
            if event.type == pg.KEYDOWN and event.key == pg.K_a:
                if len(shield) == 0 and combo.value >= 10:  # comboが10以上なら
                    combo.value -= 10
                    shield.add((Shield(bird, 400)))

        screen.blit(bg_image, [0, 0])
        gravity_group.update()  # gravityのGroupオブジェクトに含まれるインスタンスをすべて更新
        gravity_group.draw(screen)  # gravityのGruopに含まれるインスタンスをすべて描画
        
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())
        
        if tmr == 3000:  # 3000フレーム後に、ボスを登場させる
            boss = Boss()
        
        if tmr > 3500:  # 3500フレーム経過後に衝突判定を行う
            boss.update(screen)
            for beam in pg.sprite.spritecollide(boss, beams, True):
                boss_attack -= 1  # 攻撃カウントを加算
                exps.add(Explosion(beam, 100))  # 爆発エフェクト
                if combo.inc_comb(time.time()):
                    combo.value += 1  # 1コンボ＋
            if boss_attack <= 0:  # ボスに10回攻撃したら
                boss = None
                score.update(screen)
                # GameClear表示
                go_text = font_go.render("Game Clear", True, (0))
                go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(go_text , go_rect)
                pg.display.update()
                time.sleep(3)
                return

        if tmr >= 500:  # 500フレーム以上経過しているかつ
            if tmr%500 == 0:  # 500フレームに1回、コインを出現させる
                coins.add(Coin())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            if combo.inc_comb(time.time()):
                combo.value += 1  # 1コンボ＋
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            if combo.inc_comb(time.time()):
                combo.value += 1  # 1コンボ＋
                
        for bomb in pg.sprite.groupcollide(bombs, shield, True, False).keys():
            exps.add(Explosion(bomb, 100))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            if combo.inc_comb(time.time()):
                combo.value += 1  # 1コンボ＋
        
        for bomb in pg.sprite.groupcollide(bombs, gravity_group, True, False).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            if combo.inc_comb(time.time()):
                combo.value += 1  # 1コンボ＋
            
        for emy in pg.sprite.groupcollide(emys, gravity_group, True, False).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            if combo.inc_comb(time.time()):
                combo.value += 1  # 1コンボ＋
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        if pg.sprite.spritecollide(bird, coins, True):
            combo.value += 10  # コンボに10点追加

        # 爆弾があたったらLifeを削り、少し爆発を起こす
        for bomb in pg.sprite.spritecollide(bird, bombs, True): 
                exps.add(Explosion(bomb,10,scale=0.7))
                life -= 1
                bird.change_img(8, screen)
                # Life切れの場合                
                if life <= 0 :  
                    score.update(screen)
                    # GameOver表示
                    go_text = font_go.render("Game Over", True, (0))
                    go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(go_text , go_rect)
                    pg.display.update()
                    time.sleep(2)
                    return  
        # HP表示    
        for i in range(life):
            screen.blit(life_icon, (1050 - i * 40, 10))
        hp_text = font_hp.render(f"HP×{i+1}", True, (255, 255, 255))  # テキスト描画
        screen.blit(hp_text, (970- i*40, 30))

        # 描画等の更新
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        timed.update(screen)
        # coins.update(screen)
        coins.draw(screen)
        exps.update()
        exps.draw(screen)
        shield.update()
        shield.draw(screen)
        score.update(screen)
        combo.update(screen)
        emp.update()
        emp.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()