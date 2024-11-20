## Dependencies
GDSS is built in **Python 3.7.0** and **Pytorch 1.10.1**. Please use the following command to install the requirements:
```sh
pip install -r requirements.txt
```
For molecule generation, additionally run the following command:
```sh
conda install -c conda-forge rdkit=2020.09.1.0
```

If you're having trouble installing rdkit, you can try:
```sh
pip install rdkit==2022.3.5
```
## Running Experiments
### 1. Preparations
In this repository, we only provide the molecular graph dataset QM9, and other datasets and other papers will be released after they are received. To preprocess the molecular graph datasets for training models, run the following command:
```sh
python data/preprocess.py --dataset ${dataset_name}
python data/preprocess_for_nspdk.py --dataset ${dataset_name}
```
For the evaluation of generic graph generation tasks, run the following command to compile the ORCA program (see [http://www.biolab.si/supp/orca/orca.html](http://www.biolab.si/supp/orca/orca.html)):
```sh
cd evaluation/orca 
g++ -O2 -std=c++11 -o orca orca.cpp
```
### 2. Configurations
The configurations are provided on the `config/` directory in `YAML` format. 
### 3. Training
We provide a pre-trained GDSS score network under checkpoints/QM9 named gdss_qm9. We also provide a pre-trained fake score network under checkpoints/QM9 called gdss_qm9_fake.

If you want to train your sham score network, generate 50K molecules based on the GDSS-PC Sampler and train on this batch of generated data:
```sh
CUDA_VISIBLE_DEVICES=0,1 python main.py --type train --config qm9 --seed 42
```
Once you have trained your fake score network, change the value of the ckpt_f in config/sample_qm9.yaml to the name of your fake score network. In particular, depending on the GDSS settings, the score network you trained will also be saved under checkpoints/QM9, so don't worry about the path.
Note: As described in our paper, we are using the GDSS baseline model to generate new training data, not our improved model to generate training data.
### 4. Generation and Evaluation
To generate graphs using S++, run the following command:
```sh
CUDA_VISIBLE_DEVICES=${gpu_ids} python main.py --type sample --config sample_qm9 --scaler1 1.15 --scaler1 1.09
```
where scaler1 represents $\lambda_1$ in the paper, and scaler2 represents $w_1$ in the paper. In QM9's experiments, we do not recommend correcting the score during sampling, as this will result in more NFE but only a slight gain. So, in this version, $\lambda_1$ is always 0 and $w_2$ is always 1.

If you want to save the results of the presampling for direct use in subsequent samples, replace the solver.py (in the form of a copy) with the content of the solver_pre_data.py. Then navigate to the get_pc_sampler function in the solver.py and modify the path of the following code to the path you want:
```py
torch.save(x, "./pre_data/x_pre_qm9.pth")
torch.save(adj, "./pre_data/adj_pre_qm9.pth")
torch.save(flags, "./pre_data/flags_pre_qm9.pth")
```
Then, please run:
```sh
CUDA_VISIBLE_DEVICES=${gpu_ids} python main.py --type sample --config sample_qm9 --scaler1 1.15 --scaler1 1.09
```
Finally, replace the solver.py with solver_with_pre.py (in the form of a copy) and modify the path in the function get_pc_sampler to save the presampled results for you:
```py
x = torch.load("./pre_data/x_pre_qm9.pth")
adj = torch.load("./pre_data/adj_pre_qm9.pth")
flags = torch.load("./pre_data/flags_pre_qm9.pth")
```
Congratulations, you can start sampling from this new starting point for subsequent sampling, which will greatly reduce the sampling time, and this is also the version of the results we report in the paper. In particular, you can also reduce the diff_steps in the solver.py (the default value for this parameter is 1000), such as 70, and you will be surprised to find that when the starting deviation is solved, we can generate still high-quality samples in a very short time step.