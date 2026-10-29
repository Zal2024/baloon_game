## Cara menjalankan

```bash
cd ~/ros2_ws
colcon build --packages-select baloon_game
source install/setup.bash
ros2 launch baloon_game game.launch.py
```

## Penjelasan arsitektur

**node:**
- camera_node: mendapatkan input dari webcam dan mengpublish input nya.
- game_node: mencari tangan menggunakan YOLO, menggerakan bola, dan menyimpan skor.

**topic:**
- /camera/image_raw mengambil input dari camera_node ke game_node
- /game/score mengirim skor dari gamenode
- /game/debug_image mengirim gambar anotasi bounding box

**parameter:** tempat buat penyimpanan variabel (ball_speed, num_balls, hold_duration, ball_radius, etc)



## keputusan desain
saya menggunakan python karena menurut saya lebih gampang untuk dibaca dan debugging. dan untuk tambahan, saya menggunakan YOLO karena sudah terlanjur training(2 jam menggunakan Notebook (A100)). 🏃

## kendala yang saya hadapi
karena saya menggunakan YOLO masalah yang saya hadapi adalah hasil nya yang kurang memuaskan. awal nya menggunakan 500 gambar dan menggunakan settingan yang kurang(terutama penggunaan saturation membuat gambar terlihat kurang jelas). dan saya mengubah dataset dengan dataset yang suda ada di roboflow. yakni dataset yang memiliki ~8 ribu gambar, dan saya training dengan epoch 150. hasil dengan dataset 8 ribu gambar dengan epoch 150 mendapatkan weight YOLO yang akurat.

## Video
link: https://youtube.com/shorts/lSQ100SWq3A
## Bonus
saya menambahkan GUI "score:"
## rqt graph

<img width="634" height="175" alt="image" src="https://github.com/user-attachments/assets/c6f48e3c-3b09-4883-9816-441f11bbb598" />

## hasil yolo
<img width="2400" height="1200" alt="results (1)" src="https://github.com/user-attachments/assets/4fde3f4a-1def-45b4-a8aa-e19ef9e3656b" />

