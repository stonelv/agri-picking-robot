# Agricultural Picking Robot Control Program

## Overview
This project is designed to control an agricultural picking robot equipped with a Gemini335 depth camera. The robot captures video feed for analysis and generates movement coordinates for its robotic arm and base vehicle.

## Project Structure
```
agri-picking-robot
├── src
│   ├── main.py
│   ├── camera
│   │   └── gemini335.py
│   ├── robot
│   │   ├── arm_controller.py
│   │   └── base_controller.py
│   ├── analysis
│   │   └── model_interface.py
│   ├── utils
│   │   └── helpers.py
│   └── config
│       └── settings.py
├── requirements.txt
├── README.md
└── setup.py
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd agri-picking-robot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Components
- **Camera**: The `Gemini335` class in `src/camera/gemini335.py` handles video capture and processing from the depth camera.
- **Robot Control**: 
  - The `ArmController` class in `src/robot/arm_controller.py` manages the robotic arm's movements.
  - The `BaseController` class in `src/robot/base_controller.py` controls the base vehicle's movements.
- **Analysis**: The `ModelInterface` class in `src/analysis/model_interface.py` interacts with the analysis model to generate movement coordinates based on the video feed.
- **Utilities**: Helper functions for various tasks are located in `src/utils/helpers.py`.
- **Configuration**: Project settings, including camera parameters and robot specifications, are defined in `src/config/settings.py`.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.