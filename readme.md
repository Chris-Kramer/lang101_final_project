# Assignment 6 - Text classification using Deep Learning
**Christoffer Kramer**  
**20-04-2021**  
In class this week, we've seen how deep learning models like CNNs can be used for text classification purposes. For your assignment this week, I want you to see how successfully you can use these kind of models to classify a specific kind of cultural data - scripts from the TV series Game of Thrones.  
You can find the data here: https://www.kaggle.com/albenft/game-of-thrones-script-all-seasons  
In particular, I want you to see how accurately you can model the relationship between each season and the lines spoken. That is to say - can you predict which season a line comes from? Or to phrase that another way, is dialogue a good predictor of season?  
Start by making a baseline using a 'classical' ML solution such as CountVectorization + LogisticRegression and use this as a means of evaluating how well your model performs. Then you should try to come up with a solution which uses a DL model, such as the CNNs we went over in class.

## Approach and results
I started out trying to predict the season based on the lines spoken. This turned out to be difficult (if not impossible) to get anything much better than to 18-26% F1 score. 
I therefore tried to predict which house (dynasty) the character belonged to based on the lines spoken. This turned out to create slightly better results. Intuitively this makes some sense, since characters from the same house do share common phrases (such as their family motto) and they tend to talk to the same characters (which means that they are more likely to mention the names of these characters). however, the results still weren't getting any better than 20-35%. So my guess was that when the text is divided by lines spoken (effectively short sentences) the likelyhood of a line containing the family motto or characters related to the house are so low, that the model won't discover the connection.  
I, therefore, tried to divide the data by episode and house. I concactinated all the lines spoken by characters from the same house by episode. This resulted in better results, however, the F1 score was still in the 40s. However I discoverede that some houses was only present in very few episodes. So I filtered out houses that didn't appear in more than 50 episodes. This resulted in better results and performs around 60-68% percent acccuracy, and by keeping the current architecture and tweaking the parameters I believe it is possible to get it up to 72% (the highest result I got), which is why I have supplied the script with a lot of arguments that can be tweaked. 

### Problems 
One of the biggest problems for both models is the tendency to overfit. Even though I used dropout layers and regularization my cnn model still overfitted. I think the biggest problem here is simply a lack of data. Each house can't have more than 72 data points, which is a big problem, considering that it is impossible to get more data. This is problematic when testing, since some houses might only have 8 data points for validation. It might be possible to get better results by slicing up the data in half episodes since this will create more datapoints (which might make the test results more robust), but this is pure speculation and I haven't tested it.
Another consistent problem I came across is that the logistic regression model consistently performs better (above 70%), this is surprising since it only looks at word distributions rather than word embeddings.

### Personal speculation
If I were to take a guess as to why the logistic regression model performs better  I would say that is it because that word distributions are actually more relevant for this task than the semantic information which are included in the word embeddings. Neither the show nor the books really makes it explicit how characters from different houses speak. Differences in speaking patterns in Westerous tend to be regional and very superficial and (as far as I remember) the books are mainly concerned with language differences rather than dialects.  
Simple word distributions are probably very effective, since they capture how often words from the family mottos are used and how often characters that are in close proximity to the house are mentioned. Which in this context probably is a better indicator as to which house the text represents. However, this is pure speculation, and I might be completely wrong.  
However I do believe that it is possible to create deep learning model, which performs better than the logistic regression model. But compared to the work that needs to be done (and how well the logistic regression classifier actually works) it might be relevant to ask if the logistic regression is good enough.  


## Running the script


### How to run  
**Step 1: Clone repo**  
- open terminal  
- Navigate to destination for repo  
- type the following command  
```console
 git clone https://github.com/Chris-Kramer/language_assignments.git
```  
**step 2: Run bash script:**  
- Navigate to the folder "assignment-6".  
```console
cd assignment-6
```  
- Use the bash script _run_cnn-GOT.sh_ to set up environment, install dependencies, download and unzip the glove embeddings, and run the cnn model:  
```console
bash run_cnn-GOT.sh
```  
- For logistic regression use the bash script _run_logistic_regression_GOT.sh_ to set up environment, install dependencies and run the logistic regression classifier:
```console
bash run_logistic_regression_GOT.sh
```

### Output
All output will be located in the folder "output". The cnn model will output a plot over its performance and a picture of its architecture. The logistic regression classifier will output a confusion matrix and the results from cross validation. 

### Parameters: Cnn model
There are a lot of parameters, but they all fit in this architecture:
![image](pic-readme.png)  

The parameters for cnn are the following:
- `n_episodes` How many episodes a house at least should appear in.  
    - DEFAULT: 50  
- `test_size` The size of the test data as a percentage. The training size will be adjusted automatically.  
    - DEFAULT: 0.2  
- `padding` The padding type to be used when preprocessing data.  
    - DEFAULT: post  
- `num_words` How many unique words the embedding dictionary should contain.  
    - DEFAULT: 10000  
- `embedding_dim` How many embedding dimensions should embedding matrix contain? Remember to use an appropriate embedding file!  
    - DEFAULT: 100  
- `pretrained_embeddings` Which of the Glove pretrained embeddings should be used? The embedding file must be located in the folder "data/glove".  
    - DEFAULT: glove.6B.100d.txt  
- `l1` The learning rate for L1 regularization (used in the first dense layer called "Dense" on the picture above).  
    - DEFAULT: 0.0001
- `l2` The learning rate for L2 regularization (used in the Conv1D layer).  
    - DEFAULT: 0.0001  
- `trainable` Should the embeddings be trainable? Can only be True or False.  
    - DEFAULT: True  
- `filters` How many filters should there be in the Conv1D and hidden dense layer. The input is a list of ints. The first value represents the filters for the Conv1D layer while the second value is the first Dense layer.  
    - DEFAULT: 70 30  
- `dropout_rate` The dropout rate for the first and second layer. The input is a list of floats. The first value represents the dropout rate for the first dropout layer, while the second value represents the dropout rate for the second layer.  
    - DEFAULT: 0.2 0.2  
- `epochs` Amount of epochs the model should run.  
    - DEFAULT: 25  
- `batch_size` The batch size for training and evaluation.  
    - DEFAULT: 10  
    
EXAMPLE:
```console
bash run_cnn-GOT.sh --n_episodes 60 --test_size 0.1 --embedding_dim 50 --pretrained_embeddings glove.6B.50d.txt 
```

### Parameters: Logistic regression
The parameters for logistic regression are the following: 
- `n_episodes` How many episodes a house at least should appear in.  
    - DEFAULT: 50  
- `test_size` The size of the test data as a percentage. The training size will be adjusted automatically.  
    - DEFAULT: 0.2  
- `n_splits` The number of shufflesplits during the cross validation.  
    - DEFAULT: 50  
```console
bash run_logistic_regression_GOT.sh --n_episodes 60 --test_size 0.1 --n_splits 40
```

## Running on windows
This script have not been tested on a Windows machine and the bash script is made for Linux/mac users. If you're running on a local windows machine, and don't have an Unix shell with bash, you have to set up a virtual environment, activate it and install dependencies (requirements.txt). You also have to download the glove embeddings from here http://nlp.stanford.edu/data/glove.6B.zip and unzip the data in the folder "data/glove". After that you should be able to run the python scripts from the terminal since the script will handle paths in different operating systems automatically. 