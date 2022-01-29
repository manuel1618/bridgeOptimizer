# BridgeOptimizer -Bridge Constructor meets Altair Hyperworks

## Backstory

I recently played a bit with the BridgeConstructor game (e.g. here in Steam: https://bit.ly/3JNIREJ) and thought about a way to automatically get a solution proposal by using an FEM solver. This opened the door to a whole learning journey and this repository is the code basis for that. 
I upload mostly once a week a video on youtube about the recent features (https://www.youtube.com/watch?v=Zr6TJHeOJZA&list=PLE4jpqcRJiBqo8qWxV9zBuiBmEEYeb-A1)

## Basic Idea (29.01.2022)

### Problem Setup (the game)

The game consists of a 2d plane where one can place elements of different lengths. Each elements costs a basic amount + a variable amount per length. For now, lets assume all elements are equal though that will change later in the game. The goal is to construct a driving lane as well as a supporting structure as shown below. 

![grafik](https://user-images.githubusercontent.com/9959248/151668595-048e0f61-3ead-47f6-83d9-ff5cc0c43f3b.png)
![grafik](https://user-images.githubusercontent.com/9959248/151668670-a77e623a-69ea-4695-ac12-d95073313161.png)


### Idea

The structure which is searched for in this problem setup can be modelled as a 1D FEM model with rods (rods only transfer tensile and compression forces, no bending). As the gird shows a limited number of possible elements, the optimization procedure can be done by specifying a design space with all (possible / wanted) elements and let the solver decide, which elements to keep. 
The optimization goal in the game is the total cost of the bridge design, but this is not trivial to implement in the optimization solver. As an easy attempt, one might think of minimizing the mass and specifying a displacement constraint / stress constraint). Loading is also non trivial, as a gravity alone won't do it, as a bridge design with no mass would satisfy the displacement constraint (no mass equals no displacement). 

So the following assumptions were made: 

- Optimization goal: Minimize mass
- Driving lane: Build a driving lane with as few element as possible
- For each node in the driving lane put a force on it and constrain its displacement (dependent on the displacement of the full design space (i.e. all elements)) 

### Post Processing

The optimization run should be ultimately completely automated. This way, multiple variants of bridges with different design spaces can be evaluated. Cost calculation should happen as well.








