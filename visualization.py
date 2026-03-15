import matplotlib.pyplot as plt
import os

def generate_skill_chart(skills):

    if not skills:
        return

    plt.figure()
    plt.bar(skills, [1] * len(skills))
    plt.xticks(rotation=45)
    plt.title("Extracted Skills")
    plt.tight_layout()

    # Save inside static folder
    chart_path = os.path.join("static", "skills.png")
    plt.savefig(chart_path)
    plt.close()

    return chart_path
