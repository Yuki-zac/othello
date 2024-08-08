import tkinter as tk
import tkinter.messagebox
import random

# キャンバスの横方向・縦方向のサイズ（px）
CANVAS_SIZE = 400

# 横方向・縦方向のマスの数
NUM_SQUARE = 8

# 色の設定
BOARD_COLOR = 'green'  # 盤面の背景色
YOUR_COLOR = 'black'  # あなたの石の色
COM_COLOR = 'white'  # 相手の石の色
PLACABLE_COLOR = 'yellow'  # 次に石を置ける場所を示す色

# プレイヤーを示す値
YOU = 1
COM = 2

class Othello():
    def __init__(self, master):

        self.master = master  # 親ウィジェット
        self.player = YOU  # 次に置く石の色
        self.board = None  # 盤面上の石を管理する２次元リスト
        self.color = {  # 石の色を保持する辞書
            YOU: YOUR_COLOR,
            COM: COM_COLOR
        }

        # ウィジェットの作成
        self.createWidgets()

        # イベントの設定
        self.setEvents()

        # オセロゲームの初期化
        self.initOthello()

    def createWidgets(self):

        # スコアラベルの作成
        self.score_label = tk.Label(self.master, text="あなた: 2, 相手: 2", font=("Arial", 16))
        self.score_label.pack()

        # ターンラベルの作成
        self.turn_label = tk.Label(self.master, text="あなたの番です", font=("Arial", 16))
        self.turn_label.pack()

        # キャンバスの作成
        self.canvas = tk.Canvas(
            self.master,
            bg=BOARD_COLOR,
            width=CANVAS_SIZE + 1,  # +1は枠線描画のため
            height=CANVAS_SIZE + 1,  # +1は枠線描画のため
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

        # リセットボタンの作成
        self.reset_button = tk.Button(self.master, text="リセット", command=self.initOthello)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # ヘルプボタンの作成
        self.help_button = tk.Button(self.master, text="ヘルプ", command=self.showHelp)
        self.help_button.pack(side=tk.RIGHT, padx=10)

    def setEvents(self):

        # キャンバス上のマウスクリックを受け付ける
        self.canvas.bind('<ButtonPress>', self.click)

    def initOthello(self):
        '''ゲームの初期化を行う'''

        #プレイヤーを初期化
        self.player = YOU #あなたからスタート
        
        # 盤面上の石を管理する２次元リストを作成（最初は全てNone）
        self.board = [[None] * NUM_SQUARE for _ in range(NUM_SQUARE)]

        # １マスのサイズ（px）を計算
        self.square_size = CANVAS_SIZE // NUM_SQUARE

        # キャンバスをクリア
        self.canvas.delete("all")

        # マスを描画
        for y in range(NUM_SQUARE):
            for x in range(NUM_SQUARE):
                # 長方形の開始・終了座標を計算
                xs = x * self.square_size
                ys = y * self.square_size
                xe = (x + 1) * self.square_size
                ye = (y + 1) * self.square_size

                # 長方形を描画
                tag_name = 'square_' + str(x) + '_' + str(y)
                self.canvas.create_rectangle(
                    xs, ys,
                    xe, ye,
                    tag=tag_name
                )

        # 初期の石を配置
        self.placeInitialStones()

        # 最初に置くことができる石の位置を取得
        placable = self.getPlacable()

        # その位置を盤面に表示
        self.showPlacable(placable)

        # スコアラベルとターンラベルを更新
        self.updateScore()
        self.updateTurnLabel()

    def placeInitialStones(self):
        '''初期の石を配置する'''

        # あなたの石の初期位置
        self.drawDisk(3, 3, self.color[COM])
        self.drawDisk(3, 4, self.color[YOU])
        self.drawDisk(4, 3, self.color[YOU])
        self.drawDisk(4, 4, self.color[COM])

    def drawDisk(self, x, y, color):
        '''(x,y)に色がcolorの石を置く（円を描画する）'''

        # (x,y)のマスの中心座標を計算
        center_x = (x + 0.5) * self.square_size
        center_y = (y + 0.5) * self.square_size

        # 中心座標から円の開始座標と終了座標を計算
        xs = center_x - (self.square_size * 0.8) // 2
        ys = center_y - (self.square_size * 0.8) // 2
        xe = center_x + (self.square_size * 0.8) // 2
        ye = center_y + (self.square_size * 0.8) // 2

        # 円を描画する
        tag_name = 'disk_' + str(x) + '_' + str(y)
        self.canvas.create_oval(
            xs, ys,
            xe, ye,
            fill=color,
            tag=tag_name
        )

        # 描画した円の色を管理リストに記憶させておく
        self.board[y][x] = color

    def getPlacable(self):
        '''次に置くことができる石の位置を取得'''

        if self.player is None:
            return []
        
        placable = []

        for y in range(NUM_SQUARE):
            for x in range(NUM_SQUARE):
                # (x,y) の位置のマスに石が置けるかどうかをチェック
                if self.checkPlacable(x, y):
                    # 置けるならその座標をリストに追加
                    placable.append((x, y))

        return placable

    def checkPlacable(self, x, y):
        '''(x,y)に石が置けるかどうかをチェック'''

        # その場所に石が置かれていれば置けない
        if self.board[y][x] != None:
            return False

        if self.player == YOU:
            other = COM
        else:
            other = YOU

        # (x,y)座標から縦横斜め全方向に対して相手の石が裏返せるかどうかを確認
        for j in range(-1, 2):
            for i in range(-1, 2):

                # 真ん中方向はチェックしてもしょうがないので次の方向の確認に移る
                if i == 0 and j == 0:
                    continue

                # その方向が盤面外になる場合も次の方向の確認に移る
                if x + i < 0 or x + i >= NUM_SQUARE or y + j < 0 or y + j >= NUM_SQUARE:
                    continue

                # 隣が相手の色でなければその方向に石を置いても裏返せない
                if self.board[y + j][x + i] != self.color[other]:
                    continue

                # 置こうとしているマスから遠い方向へ１マスずつ確認
                for s in range(2, NUM_SQUARE):
                    # 盤面外のマスはチェックしない
                    if x + i * s >= 0 and x + i * s < NUM_SQUARE and y + j * s >= 0 and y + j * s < NUM_SQUARE:

                        if self.board[y + j * s][x + i * s] == None:
                            # 自分の石が見つかる前に空きがある場合
                            # この方向の石は裏返せないので次の方向をチェック
                            break

                        # その方向に自分の色の石があれば石が裏返せる
                        if self.board[y + j * s][x + i * s] == self.color[self.player]:
                            return True

        # 裏返せる石がなかったので(x,y)に石は置けない
        return False

    def showPlacable(self, placable):
        '''placableに格納された次に石が置けるマスの色を変更する'''

        for y in range(NUM_SQUARE):
            for x in range(NUM_SQUARE):
                # fillを変更して石が置けるマスの色を変更
                tag_name = 'square_' + str(x) + '_' + str(y)
                if (x, y) in placable:
                    self.canvas.itemconfig(tag_name, fill=PLACABLE_COLOR)
                else:
                    self.canvas.itemconfig(tag_name, fill=BOARD_COLOR)

    def click(self, event):
        '''盤面がクリックされた時の処理'''

        if self.player != YOU:
            # COMが石を置くターンの時は何もしない
            return

        # クリックされた位置がどのマスであるかを計算
        x = event.x // self.square_size
        y = event.y // self.square_size

        if self.checkPlacable(x, y):
            # 次に石を置けるマスであれば石を置く
            self.place(x, y, self.color[self.player])

    def place(self, x, y, color):
        '''(x,y)に色がcolorの石を置く'''

        # (x,y)に石が置かれた時に裏返る石を裏返す
        self.reverse(x, y)

        # (x,y)に石を置く（円を描画する）
        self.drawDisk(x, y, color)

        # スコアラベルを更新
        self.updateScore()

        # 次に石を置くプレイヤーを決める
        before_player = self.player
        self.nextPlayer()

        if before_player == self.player:
            # 前と同じプレイヤーであればスキップされたことになるのでそれを表示
            if self.player != YOU:
                tk.messagebox.showinfo('結果', 'あなたのターンをスキップしました')
            else:
                tk.messagebox.showinfo('結果', '相手のターンをスキップしました')
        elif not self.player:
            # 次に石が置けるプレイヤーがいない場合はゲーム終了
            self.showResult()
            return
        
        #プレイヤーがいる場合のみ次の処理を行う
        if self.player:
            # 次に石がおける位置を取得して表示
            placable = self.getPlacable()
            self.showPlacable(placable)

            # ターンラベルを更新
            self.updateTurnLabel()

            if self.player == COM:
                # 次のプレイヤーがCOMの場合は1秒後にCOMに石を置く場所を決めさせる
                self.master.after(1000, self.com)

    def reverse(self, x, y):
        '''(x,y)に石が置かれた時に裏返す必要のある石を裏返す'''

        if self.board[y][x] is not None:
            # (x,y)にすでに石が置かれている場合は何もしない
            return

        if self.player == COM:
            other = YOU
        else:
            other = COM

        for j in range(-1, 2):
            for i in range(-1, 2):
                # 真ん中方向はチェックしてもしょうがないので次の方向の確認に移る
                if i == 0 and j == 0:
                    continue

                if x + i < 0 or x + i >= NUM_SQUARE or y + j < 0 or y + j >= NUM_SQUARE:
                    continue

                # 隣が相手の色でなければその方向で裏返せる石はない
                if self.board[y + j][x + i] != self.color[other]:
                    continue

                # 置こうとしているマスから遠い方向へ１マスずつ確認
                for s in range(2, NUM_SQUARE):
                    # 盤面外のマスはチェックしない
                    if x + i * s >= 0 and x + i * s < NUM_SQUARE and y + j * s >= 0 and y + j * s < NUM_SQUARE:

                        if self.board[y + j * s][x + i * s] is None:
                            # 自分の石が見つかる前に空きがある場合
                            # この方向の石は裏返せないので次の方向をチェック
                            break

                        # その方向に自分の色の石があれば石が裏返せる
                        if self.board[y + j * s][x + i * s] == self.color[self.player]:
                            for n in range(1, s):
                                # 盤面の石の管理リストを石を裏返した状態に更新
                                self.board[y + j * n][x + i * n] = self.color[self.player]

                                # 石の色を変更することで石の裏返しを実現
                                tag_name = 'disk_' + str(x + i * n) + '_' + str(y + j * n)
                                self.canvas.itemconfig(
                                    tag_name,
                                    fill=self.color[self.player]
                                )
                            break

    def nextPlayer(self):
        '''次に石を置くプレイヤーを決める'''

        before_player = self.player

        # 石を置くプレイヤーを切り替える
        if self.player == YOU:
            self.player = COM
        else:
            self.player = YOU

        # 切り替え後のプレイヤーが石を置けるかどうかを確認
        placable = self.getPlacable()

        if len(placable) == 0:
            # 石が置けないのであればスキップ
            self.player = before_player

            # スキップ後のプレイヤーが石を置けるかどうかを確認
            placable = self.getPlacable()

            if len(placable) == 0:
                # それでも置けないのであれば両者とも石を置けないということ
                self.player = None
                #ゲームの終了処理を行う
                self.showResult()

    def updateScore(self):
        '''現在のスコアを表示する'''
        num_your = sum(row.count(YOUR_COLOR) for row in self.board)
        num_com = sum(row.count(COM_COLOR) for row in self.board)
        self.score_label.config(text=f"あなた: {num_your}, 相手: {num_com}")

    def updateTurnLabel(self):
        '''現在のターンを表示する'''
        if self.player == YOU:
            self.turn_label.config(text="あなたの番です")
        elif self.player == COM:
            self.turn_label.config(text="相手の番です")
        else:
            self.turn_label.config(text="ゲーム終了！")

    def showResult(self):
        '''ゲーム終了時の結果を表示する'''

        num_your = sum(row.count(YOUR_COLOR) for row in self.board)
        num_com = sum(row.count(COM_COLOR) for row in self.board)

        if num_your > num_com:
            result = "あなたの勝ちです!"
        elif num_your < num_com:
            result = "相手の勝ちです..."
        else:
            result = "引き分け"

        tk.messagebox.showinfo('結果', f'あなた: {num_your}, 相手: {num_com}\n{result}')

        #ゲーム終了後、リセットボタンを押すことでまた対局を始められる
        self.player = YOU
        
    def showHelp(self):
        '''ヘルプを表示する'''
        help_message = (
            "オセロゲーム\n\n"
            "ルール:\n"
            "1. プレイヤーは交互に石を打ちます。\n"
            "2. 石を打つとき、自分の色の石で相手の色の石を挟めるマスに打ちます。たて・よこ・ななめのどの方向に挟んでもいいです。挟んだ石は全てひっくり返し、自分の色の石にします。\n"
            "3. 相手の石を挟めるマスが無い場合はパスになります。打てるマスがくるまでは何度もパスとなり、相手が連続して打ちます。\n"
            "4. 盤面がぜんぶ埋まるか、黒白ともに打つマスがなくなったら終了です。自分の石が多い方が勝ちとなります。\n\n"
            "コントロール:\n"
            "- マスをクリックして石を打ちます。\n"
            "- 'リセット'ボタンを押すことで新しい対局を始められます。\n"
            "- 'ヘルプ'ボタンを押すことでヘルプ画面が表示されます。"
        )
        tk.messagebox.showinfo("ヘルプ", help_message)

    def com(self):
        '''COMに石を置かせる'''

        # 石が置けるマスを取得
        placable = self.getPlacable()

        # 石を置く最適な場所を決定する
        best_move = self.findBestMove(placable)
        if best_move:
            x, y = best_move
            # 石を置く
            self.place(x, y, COM_COLOR)

    def findBestMove(self, placable):
        '''最適な手を見つける'''
        best_score = -float('inf')
        best_move = None

        for x, y in placable:
            # 仮にこの位置に石を置いた場合の評価を計算する
            score = self.evaluateMove(x, y)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move

    def evaluateMove(self, x, y):
        '''石を置く手を評価する（角を優先し、反転数を重視）'''
        score = 0

        # 角の位置なら高評価
        if (x == 0 and y == 0) or (x == 0 and y == NUM_SQUARE-1) or (x == NUM_SQUARE-1 and y == 0) or (x == NUM_SQUARE-1 and y == NUM_SQUARE-1):
            score += 100

        # 最大反転数を評価
        original_board = [row[:] for row in self.board]
        original_player = self.player

        self.board[y][x] = self.color[self.player]
        self.reverse(x, y)
        flipped_count = sum(row.count(self.color[self.player]) for row in self.board) - sum(row.count(self.color[original_player]) for row in original_board)

        # 元に戻す
        self.board = original_board
        self.player = original_player

        score += flipped_count

        return score

# スクリプト処理ここから
app = tk.Tk()
app.title('Othello')
othello = Othello(app)
app.mainloop()