<img width="634" height="175" alt="image" src="https://github.com/user-attachments/assets/5a71d459-5846-4b78-bc4c-acd6a5bf0292" />cara menjalankan:

cd ~/ros2_ws
colcon build --packages-select baloon_game
source install/setup.bash
ros2 launch baloon_game game.launch.py


penjelasan arsitektur:
node: camera_node: mendapatkan input dari webcam dan mengpublish input nya.
      game_node: mencari tangan menggunakan YOLO, menggerakan bola, dan menyimpan skor.

topic: /camera/image_raw mengambil input dari camera_node ke game_node
      /game/score menyimpan skor
      /game/debug_image menambahkan bounding box

parameter: tempat buat penyimpanan variabel (ball_speed, num_balls, hold_duration, ball_radius, etc)

video: 

rqt graph: <img width="634" height="175" alt="image" src="https://github.com/user-attachments/assets/c6f48e3c-3b09-4883-9816-441f11bbb598" />
