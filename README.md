# Fossbot Gazebo Simulation Package

[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Ignition%20Fortress-orange)](https://ignitionrobotics.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


**Fossbot Gazebo** is a complete ROS2 simulation package for the Fossbot robot with support for SLAM, autonomous navigation (NAV2), and RTAB-Map visual SLAM.

---

## Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
  - [Step 1: Install Ubuntu 22.04](#step-1-install-ubuntu-2204)
  - [Step 2: Install ROS2 Humble](#step-2-install-ros2-humble)
  - [Step 3: Install Ignition Gazebo Fortress](#step-3-install-ignition-gazebo-fortress)
  - [Step 4: Install ROS-GZ Bridge](#step-4-install-ros-gz-bridge)
  - [Step 5: Clone and Build](#step-5-clone-and-build)
  - [Step 6: Install Dependencies](#step-6-install-dependencies)
  - [Step 7: After Code Changes](#-after-changes-to-code)
- [Usage](#-usage)
  - [Main Menu](#main-menu)
  - [Individual Commands](#individual-commands)
- [Teleoperation](#-teleoperation)
- [Maintainer](#-maintainer)

---

## Requirements

| Component | Version |
|-----------|---------|
| **Ubuntu** | 22.04 (Jammy) |
| **ROS2** | Humble |
| **Ignition Gazebo** | Fortress |
| **Python** | 3.10+ |
| **ROS-GZ Bridge** |  |
| **SLAM Toolbox** |  |
| **NAV2 Bringup** |  |
| **RTAB-Map** |  |

---

## Installation

### Step 1: Install Ubuntu 22.04

#### Option A: Native Installation
Follow the [official Ubuntu tutorial](https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview)

#### Option B: WSL Installation
Open PowerShell as Administrator and run:
```bash
wsl --install -d Ubuntu-22.04
```

---

### Step 2: Install ROS2 Humble

Follow the [official installation guide](https://docs.ros.org/en/humble/Installation.html)

```bash
# Locale & Repository
sudo apt update && sudo apt install curl gnupg2 lsb-release locales software-properties-common
sudo locale-gen en_US en_US.UTF-8
sudo add-apt-repository universe

# Adding the Official ROS 2 Key
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble
sudo apt update
sudo apt install ros-humble-desktop ros-dev-tools

# Environment Setting
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

### Step 3: Install Ignition Gazebo Fortress

#### Option A: Quick Install
```bash
sudo apt install gz-fortress -y
```

#### Option B: Manual Install
```bash
# Add Gazebo repository
sudo curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/gazebo-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
sudo apt update

# Install Ignition Fortress
sudo apt install gz-fortress -y
```

---

### Step 4: Install ROS-GZ Bridge

```bash
sudo apt install ros-humble-ros-gz-bridge -y
```

---

### Step 5: Clone and Build


#### Option A: Clone with Git (Recommended)
```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone repository
git clone https://github.com/VGioAnd/fossbot_gazebo.git

# Build
cd ~/ros2_ws
colcon build --packages-select fossbot_gazebo --symlink-install

# Source workspace
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```


#### Option B: Download ZIP
```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Download ZIP
wget https://github.com/VGioAnd/fossbot_gazebo/archive/refs/heads/main.zip

# Extract
unzip main.zip

# Rename folder
mv fossbot_gazebo-main fossbot_gazebo

# Clean up
rm main.zip

# Build
cd ~/ros2_ws
colcon build --packages-select fossbot_gazebo --symlink-install

# Source workspace
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### Option C: Download ZIP with Browser
1.Go to: https://github.com/VGioAnd/fossbot_gazebo

2.Click the green "Code" button

3.Select "Download ZIP"

4.Extract the downloaded ZIP file

5.Rename the extracted folder from fossbot_gazebo-main to fossbot_gazebo

6.Move the folder to: ~/ros2_ws/src/fossbot_gazebo

7.Open a terminal and run:
```bash
cd ~/ros2_ws
colcon build --packages-select fossbot_gazebo --symlink-install
source ~/ros2_ws/install/setup.bash
```


---

### Step 6: Install Dependencies

#### Option A: Automatic with rosdep
```bash
sudo rosdep init
rosdep update
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select fossbot_gazebo --symlink-install
```

#### Option B: Manual Installation
```bash
sudo apt install -y \
  ros-humble-ros-gz-bridge \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-xacro \
  ros-humble-tf2-ros \
  ros-humble-tf2-tools \
  ros-humble-slam-toolbox \
  ros-humble-rtabmap-ros \
  ros-humble-rtabmap-viz \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-rviz2 \
  ros-humble-teleop-twist-keyboard \
  ros-humble-launch \
  ros-humble-launch-ros

colcon build --packages-select fossbot_gazebo --symlink-install
```
---

### Check Dependencies Installation

```bash
ros2 pkg list | grep -E "slam_toolbox|rtabmap|nav2|robot_localization|ros_gz_bridge" && echo " OK" || echo "Missing"
```
---

### After Changes to Code

If you modify the code, rebuild with:

```bash
cd ~/ros2_ws
rm -rf build/fossbot_gazebo install/fossbot_gazebo
colcon build --packages-select fossbot_gazebo --symlink-install
```



---

## Usage

### Main Menu

```bash
ros2 run fossbot_gazebo fossbot
```

### Individual Commands

| Command | Description |
|---------|-------------|
| `ros2 run fossbot_gazebo reset` | Reset ROS2 processes |
| `ros2 run fossbot_gazebo sim` | Basic simulation |
| `ros2 run fossbot_gazebo lidarmap` | SLAM Toolbox mapping |
| `ros2 run fossbot_gazebo rtabmap` | RTAB-Map with LiDAR |
| `ros2 run fossbot_gazebo rtabcam` | RTAB-Map with camera |
| `ros2 run fossbot_gazebo nav2lidar` | NAV2 with LiDAR |
| `ros2 run fossbot_gazebo nav2uss` | NAV2 with LiDAR and ultrasonic |
| `ros2 run fossbot_gazebo nav2rtab` | NAV2 with RTAB-Map with LiDAR |
| `ros2 run fossbot_gazebo nav2cam` | NAV2 with RTAB-Map with LiDAR and camera |


---

## Teleoperation

### Control via Gazebo

In the gazebo at the top right click on the three dots, type teleop and click it. 
A navigation control will appear at the bottom right.

### Direct Velocity Commands
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.5}}"
```

---

## Package Structure

```
fossbot_gazebo/
├── fossbot_gazebo/
│   ├── scripts/          # Python scripts
│   ├── config/           # RViz configuration files
│   ├── launch/           # Launch files
│   ├── params/           # NAV2 & SLAM parameters
│   ├── maps/             # Map files (.yaml, .pgm, .db)
│   ├── models/           # Robot models (URDF, SDF, meshes)
│   └── worlds/           # Gazebo worlds
├── resource/
├── setup.py
├── setup.cfg
├── package.xml
└── README.md
```

---

## Maintainer

**VGioAnd** - [andreadakisgiorgos@yahoo.com](mailto:andreadakisgiorgos@yahoo.com)

---
