# NeuroSync 🧠🎮
## Cognitive Synchronization Game System   
**Final Project – B.Sc. in Computer Science**  
The Academic College of Tel Aviv-Yaffo  
Supervised by Dr. Sarel Cohen  

## 👥 Team Members
- Lior Kashi  
- Or Lerner  
- Daniel Shoshan  

---

## 🎓 About the Project

This project was developed as part of our final B.Sc. project in Computer Science at the Academic College of Tel Aviv-Yaffo. The system was built under the supervision of Dr. **Sarel Cohen**, in collaboration with brain researcher **Lior Noy**, whose work focuses on **cognitive synchronization between individuals**.

The system supports an experimental game designed to study cognitive synchronization through interactive tasks.

---

## 🎮 Overview

The system simulates a two-player game played on a **virtual board with 10 slots**.

- Each player takes turns moving a tile on the board.
- The goal is to create a meaningful or "coherent" **shape** during their turn.
- At specific moments, the system allows **saving** the current shape for analysis.

---

## 🤖 AI-Based Shape Classification

One of the project's core components is an **AI system** that:

- Analyzes saved shapes.
- **Categorizes** them into defined pattern types.
- Provides insight into the **cognitive patterns and strategies** of each player.

---

## 🎥 Player Identification via Camera

The system integrates a **camera-based module** to:

- Automatically detect which player is currently taking their turn.
- Enable hands-free gameplay with seamless interaction tracking.

---

## 👁️‍🗨️ Eye Movement Prediction (Optional Module)

As an advanced feature, the system includes support for:

- **Eye-tracking-based predictions**, analyzing players' gaze behavior to anticipate their actions.

---

## 🧪 Research Context

This system serves as a research tool in the study of **cognitive synchronization**, developed to support Lior Noy's research.  
By analyzing the **shapes created during gameplay** and correlating them with players' **decision-making processes**, researchers can explore how individuals align cognitively during collaborative tasks.

---

## 🚀 Getting Started
### ⚙️ Install required dependencies
Make sure to install all the necessary libraries before running the system.

To run the system locally:  

### Step 1 – Clone the repository
\`\`\`bash
git clone https://github.com/liork98/NeuroSync.git
cd NeuroSync
\`\`\`

### Step 2 – Add your OpenAI API key  
Open the file \`create_logs_table_3.py\` and insert your OpenAI API key in the designated section.  

### Step 3 – Run the pipeline  
\`\`\`bash
python run_pipeline.py
\`\`\`
