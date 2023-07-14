To run the Flask app:
- Set up the environment (I prefer `conda` as an environment manager):
  ```
  conda env create -f env.yml
  conda activate helium_env
  ```
- Run the Flask app (from the base directory `<path_to_repo>/helium/src`):
  ```
  python app.py
  ```
- Visit `<your_ip_address>:5000`