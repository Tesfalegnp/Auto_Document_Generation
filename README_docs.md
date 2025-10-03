# Project: Hebbian Learning Model

This project implements a Hebbian learning model for pattern recognition. It includes model definition, training logic, and visualization tools.

## Project Structure

The project is structured as follows:

-   **`src/`**: Contains the core logic for the Hebbian learning model, including model definition, training process, and main training script.
-   **`utils/`**: Houses utility functions, currently focusing on visualization of model parameters.
-   **`data/`**: Contains any data used. Currently, it holds a test Jupyter notebook.

## File-by-File Deep Dive

### `LICENSE`

*   **Role**: Contains the license information for the project.
*   **Language**: Unknown
*   **Key Information**: Specifies the terms under which the project can be used and distributed.

### `README.md`

*   **Role**: This file; provides an overview and documentation of the project.
*   **Language**: Unknown
*   **Key Information**: Explains the project's purpose, structure, and usage.

### `data/notebook_test.ipynb`

*   **Role**: Jupyter Notebook for testing.
*   **Language**: Unknown
*   **Key Information**: May contain example usage of the Hebbian model and visualization tools.

### `requirements.txt`

*   **Role**: Lists the Python packages required to run the project.
*   **Language**: Unknown
*   **Key Information**: Used by pip to install dependencies. Example content: `numpy==1.23.0`

### `src/hebbian.py`

*   **Role**: Defines the Hebbian model.
*   **Language**: Python
*   **Key Classes**:
    *   `HebbianModel`:
        *   `__init__(self, input_size, output_size)`: Initializes the model with a weight matrix of specified dimensions. `input_size` determines the number of input features, and `output_size` is the number of output nodes. The weights are initialized to zero.
        *   `forward(self, x)`: Performs a forward pass through the network. It takes input `x` and returns the output of the network.
        *   `update_weights(self, x, y, learning_rate)`: Updates the model weights according to the Hebbian learning rule. `x` is the input, `y` is the output, and `learning_rate` controls the magnitude of weight adjustments.

### `src/model.py`

*   **Role**: Defines an abstract `Model` class. This is a generic model parent class that could be used for any other model.
*   **Language**: Python
*   **Key Classes**:
    *   `Model`:
        *   `__init__(self)`: Initializes the model.
        *   `forward(self, x)`: Performs a forward pass through the network.
        *   `update_weights(self, x, y, learning_rate)`: Updates the model weights.
        *   `save_weights(self, path)`: Saves the model's weights to a file.
        *   `load_weights(self, path)`: Loads the model's weights from a file.

### `src/train.py`

*   **Role**: Contains the main training script.
*   **Language**: Python
*   **Key Functions**:
    *   `main()`: Orchestrates the training process. Loads data, initializes the model, trains the model, and saves the trained weights.  Also uses the visualizer class.

### `src/trainer.py`

*   **Role**: Defines the `Trainer` class.
*   **Language**: Python
*   **Key Classes**:
    *   `Trainer`:
        *   `__init__(self, model, learning_rate)`: Initializes the trainer with the model and learning rate.
        *   `train(self, x, y)`: Trains the model on a single input-output pair `(x, y)`. It performs a forward pass and updates the weights using the Hebbian learning rule.

### `utils/visualize.py`

*   **Role**: Provides visualization utilities.
*   **Language**: Python
*   **Key Classes**:
    *   `Visualizer`:
        *   `__init__(self)`: Initializes the visualizer.
        *   `plot_weights(self, weights, filename)`: Generates a heatmap visualization of the weight matrix.  Uses `matplotlib` to create and save the visualization.

## Cross-File Relationships

*   `hebbian.py` defines the `HebbianModel`, which inherits from `model.py`.
*   `trainer.py` uses the `HebbianModel` defined in `hebbian.py` to train the model.
*   `train.py` orchestrates the training process using the `Trainer` from `trainer.py` and the `HebbianModel` from `hebbian.py`.
*   `train.py` uses `visualize.py` to visualize model weights during or after training.
*   The `Model` class in `model.py` provides the basic model class that the `HebbianModel` extends.

## Getting Started

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the training script:**

    ```bash
    python src/train.py
    ```

## Output Examples

The training script `src/train.py` generates the following output:

*   **Model weights**: Saved to a file (e.g., `model_weights.pth`). The location and name depend on the implementation inside the training script.
*   **Weight visualization**: A plot of the weight matrix is saved to a file (e.g., `weights.png`).
