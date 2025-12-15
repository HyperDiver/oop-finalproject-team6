# oop-finalproject-team6


dependencies  
`pip install "gymnasium[classic_control]"  
pip install matplotlib  `

part2:

usage:  
`python3 frozen_lake.py`


part3:

目標:透過訓練讓機器人到達目的地
我們的場景中除了目的地的包裹與機器人還包含了障礙物以及輸送帶，增加機器人到達目的地的難度。

程式簡介:
grid_map:定義了地圖中所有物件的位置

grid_object:定義物件的base class以及derived class，包含障礙物、傳送帶以及目的地

robot_env:繼承自gym，定義了觀察域與行為域

trainer:負責從環境傳入的觀察域與行為域進行表格訓練

warehouse_robot:定義機器人的移動行為

usage:
`python3 main.py`

contribution table:  
戴維佑：part2, UML diagram.  
張韶軒：part3.  
王勁詠：reflection report, slide.  
