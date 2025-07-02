# Physical Solution Space (PSS) Model
The Physical Solution Space (PSS) model calculates which adaptation measures are physically feasible for implementation in deltas, based on the unique physical characteristics of the deltas. This code runs for a global dataset of 769 deltas, but a sample dataset containing 30 deltas is provided here.

## Dependencies 
- Python v3.12.4

### Packages 
- pandas

### Running the code

  1. **Clone** this git repository to your computer

     Open the command prompt, and navigate to your desired folder (the directory where you want the repository to be places). 
Run the following command to clone the repository
     ```shell
     cd my\desired\directory
     ```
     ```shell
     git clone git@github.com:kiara-lasch/Workshop_KGL.git
     ```

  2. **Create** and **Activate** environment 

     Create, activate and name the environment associated with this script 
     ``` shell
     conda env create -f environment.yml -n workshop2
     ```

  
  3. **Prepare** to run the script 

     In the command prompt, navigate to the "src" folder (the folder where the source script is located)

     ```shell
     cd src
     ```
     
  4. **Run** the script

     In the command prompt, run the following line of code to execute the script

     ```shell
     python delta_analysis.py
     ```

