_This project has been created as part
of the 42 curriculum by [aspenle[, tbelard]]_


Description project:

This project is about maze generation, we had to create the MazeGenerator module that
we can import later. The generator takes in arg a file named "config.txt" and the Parser 
Module transform that in verified data for initiate the Maze, then Window use the maze and an algorithme to generate one and display it frame per frame. As an output we return the hexadecimal representation of the finished maze followed by a list of the directions of the shortest path with the cardinal format.

Algorithm's choice: 
    -Backtracking
    -Hunt&kill
    -BinaryTree
    -Prim's

Shortest path algorithm: A-star.

Algorithm description:

    General context:
        reusability:
            All the maze algorithm use a seed to randomly choose the next cell or the next direction, so we can repeat the exact same maze with the same seed.

        Wall removal convention:
            All the cells have 4 walls and because of their proximity they share walls.
            So when we remove walls we also have to remove the opposite wall of the neighbord cell.
        
        Enums:
            We use an Enum to facilitate the moves, with Direction.delta() we grab a tuple to add to the current position to move to the next one, with Direction.oppo() we can ask for the opposite direction, thats efficient for our removals actions
            We also have a version for mlx with the % of the cell we want to set up as walls and the direction.
    
    The Backtracking algo:
        Is used as an iterative solution similar to the DFS algo, the process is to  choice a direction in a list of available from the point of view of the current cell, while we are not blocked we continue to carve the maze, else we backtrack in the current path we created until we find a new possible way to carve, the generation is finished when all the cell are visited.

    The Hunt and Kill algo:
        This one is very similar to the backtrack one, the difference is from the way to find a possible path, here from the moment we are stuck we parse the maze from the position (0, 0) to the end until we find a cell not visited AND with a visited neighbord cell, the generation is finished when the parsing mode reach the end without finding a cell who satisfact the both conditions.

    The Binary Tree Algo:
        We start at the position (0,0) and with iterate line by line opening the north or the west (when its possible) so when its not out of the maze or in the 42 pattern.
        The generation is finished when we iterated on all the cells.

    Prim's Algo:
        This one act like a wave, we choose a cell at the entry point, then we add all his validate neighbords to a list, we choice a random valid direction that we named "frontier", frontier is randomly choosen on all the valid directions who point to visited neigbords cell and we break the walls, we also add the valid neigbord of the new cell we carved to the list and we repeat until all the cells are visited

Display:
    We choose Mlx to represent our maze, we have the class: Window, Image, Color, Font, TypedText.
    Font is our own ascii representation pixel per pixel. The text editor allows us to edit the configuration text in live ! So we can use a mini terminal in the lower part of the window to configurate the parameter of the maze once again in live :).
    The scroll of course is handeled, we have a color mode "rainbow", the scale/ratio of the cell is dynamic, thus the maze always fit to the window size.

    How to use our mlx terminal:
        press escape to leave,
        press space to pause and edit the configuration
        press right entre for the step by step mode
        press n to apply the new config to the current maze
        press c to toggle the colors
        press . to directly have the finished maze
        clic to toggle the shortest path

Config rules:
    entry and exit cannot be the same
    entry and exit cannot be inside of the 42 pattern and have to be inside of the maze
    width and height have to be less than 4001
    If you write a bad algorithm name the backtrack will be use per default
    Without seed value a random value will be set
    Anim is by default True but if you put False it allows you to see the final result directly.

How to use:
    use make install to have all the environnement (pydantic, mypy, flake8, .env)
    make lint to verify the code with flake8 and mypy.
    Make run to run the maze generator.
    Enjoy the view.

Roles:
    Aspenle: he made the backtrack algo, all the mlx part, the text editor, all the display

    Tbelard: he made the hunt and kill, binary tree and prim's algos, he made the parser and the pydantic verifications 
