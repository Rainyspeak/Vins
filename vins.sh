roslaunch mavros px4.launch &sleep 10;
rosrun mavros mavcmd long 511 105 10000 0 0 0 0 0 & sleep 5;
roslaunch realsense2_camera rs_camera.launch;
exit;
#roslaunch vins vins.launch;
