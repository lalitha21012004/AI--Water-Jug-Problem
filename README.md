Interactive N-Bucket Water Transfer Solver (Heuristic DFS & Barycentric Mapping)

An interactive state-space puzzle and AI solver built in Python that generalizes the classic Water Jug Problem to N buckets. The application combines Heuristic Depth-First Search (DFS) with 2D Barycentric Coordinate Mapping to validate user moves, solve state transitions, and visualize variable trajectories in real time.

Project Structure
├── solver_engine.py   # Backend: Puzzle generation, transfer rules, Barycentric math & Heuristic DFS
├── app.py             # Frontend: Interactive Streamlit UI, live variable inspector & Matplotlib plotting
└── README.md          # Project documentation

Files Involved
solver_engine.py (Backend): Handles randomized solvable puzzle initialization, strict transfer-rule validation, barycentric coordinate normalization, and the heuristic-guided DFS solver.
app.py (Frontend): Manages user inputs ($N$ buckets, start trigger, move execution), synchronizes live backend state variables via st.session_state, and renders the 2D state trajectory using Matplotlib.


Tech Stack
Language: Python 3.x
Frontend & State Management: Streamlit
Data Visualization: Matplotlib & NumPy 
MathCore Algorithms: Heuristic Depth-First Search (DFS), Barycentric Simplex Projection, Hash-Set State 


PruningTechniques & ApproachBarycentric Coordinate Mapping:
Since water is transferred strictly between buckets without external addition or drainage during gameplay, total system volume W = ∑{i=1}^{N} v_i remains conserved. Each state vector $S = (v_1, v_2,..., v_N) is normalized into barycentric weights w_i = {v_i}{W} and projected onto a 2D regular N-gon simplex:x = ∑{i=1}^{N} w_i cos(2pi(i-1)/{N}), y = ∑{i=1}^{N} w_i sin(2pi(i-1)/{N})

Heuristic Depth-First Search (DFS):
Instead of exploring states blindly, child states generated from valid pours are ranked using a heuristic function h(S) based on Euclidean distance in barycentric space and remaining volume difference to the target. 
The most promising branches are pushed onto the stack first, cutting down unnecessary exploration.
Strict Domain Constraints:
    Allowed: Pouring from a Full bucket (v_src = c_src) into any non-full bucket.
    Allowed: Pouring from any non-empty bucket into an Empty bucket (v_dst = 0).
    Blocked: Pouring from a partially filled bucket into another partially filled bucket.
Step-by-Step:
 WorkflowInput Bucket Count (N): The user specifies the desired number of buckets (N).
 Random Capacity Generation: The backend assigns randomized maximum capacities C = [c_1, c_2, ... c_N] and initializes a verified solvable starting distribution.
 Display Setup: Initial capacities, current water levels, and target volume are displayed to the user.
 Start Trigger: Clicking the Start button locks the parameters and initializes the session state.
 Move Restriction: A maximum move limit (M_max) is enforced alongside visible transfer rules.
 Backend Rule & Heuristic Execution: On each user move, solver_engine.py validates the transfer, updates barycentric coordinates, and recalculates heuristic metrics.
 Live Variable Display: Updated state vectors, heuristic scores, and plotted coordinates refresh immediately on the frontend.
 Success State: Reaching the target volume within the move budget triggers a congratulatory completion banner.
 Retry State: Exhausting all moves displays an encouraging message prompting the user to try again.
 
 What Makes This Unique & Key AchievementsGeometric Visualization of Abstract States: Projects high-dimensional N-bucket volume states onto an intuitive 2D Matplotlib simplex trajectory rather than plain console text.
 Live Backend Transparency: Exposes internal AI solver variables (state tuples, barycentric (x, y)coordinates, and heuristic values) dynamically after every user interaction.
 Guaranteed Solvability: Pre-validates randomly generated capacities using the DFS engine before starting the game so users never face an impossible puzzle.
 
 Limitations
Closed-System Conservation: Because external taps and drains are disabled during gameplay, total water volume stays fixed; therefore, target volumes cannot exceed the initial water sum.
High N Visual Overlap: While the mathematical mapping works for any N  2D, projecting N > 6 buckets onto a 2D polygon can cause distinct states to project near overlapping (x, y) coordinates.Suboptimal Path Guarantee: Heuristic DFS finds a valid path rapidly with low memory overhead, though unlike A*, it prioritizes speed and depth over guaranteeing the absolute shortest move sequence.

How to Run Locally
# Install required dependencies
pip install streamlit matplotlib

# Launch the interactive application
streamlit run app.py

# Watch my app which is deployed on streamlit community
https://ai--water-jug-problem-xpmeq53p3dyk9kwiba4dnn.streamlit.app/
