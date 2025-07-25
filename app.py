from flask import Flask, render_template, request, jsonify
from model.performance_model import train_model, predict_performance
import traceback

app = Flask(__name__)

# Initialize model
model, label_encoder = train_model("student_performance_ml/data/student_performance_data.csv")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        try:
            # Debug: Print received form data
            print("Form Data Received:", request.form)

            # Get and validate form data
            user_input = get_form_data(request.form)
            model_input = convert_to_model_format(user_input)

            # Get prediction
            performance = predict_performance(model, label_encoder, model_input)

            # Generate personalized tips
            tips = generate_performance_tips(performance, user_input)

            return jsonify({
                'status': 'success',
                'performance': performance,
                'tips': tips,
                'user_input': {
                    'study_time': user_input['study_time'],
                    'screen_time': user_input['screen_time'],
                    'sleep': user_input['sleep'],
                    'revision': user_input['revision'],
                    'edu_youtube': user_input['edu_youtube']
                }
            }), 200

        except KeyError as ke:
            return jsonify({
                'status': 'error',
                'message': f"Missing field: {str(ke)}"
            }), 400

        except ValueError as ve:
            return jsonify({
                'status': 'error',
                'message': f"Invalid input value: {str(ve)}"
            }), 400

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f"Unexpected error: {str(e)}"
            }), 500


def get_form_data(form):
    """Extract and validate form data"""
    return {
        'study_time': float(form['study_time']),
        'screen_time': float(form['screen_time']),
        'sleep': float(form['sleep']),
        'attendance': float(form['attendance']),
        'activity': form['activity'],
        'revision': float(form['revision']),
        'distractions': int(form['distractions']),
        'edu_youtube': float(form['edu_youtube']),
        'goal': form['goal']
    }


def convert_to_model_format(user_input):
    """Convert form data to model input format"""
    return {
        "study_time_min": user_input['study_time'],
        "total_screen_time_min": user_input['screen_time'],
        "sleep_hours": user_input['sleep'],
        "class_attendance_percent": user_input['attendance'],
        "physical_activity": 1 if user_input['activity'].lower() == 'yes' else 0,
        "weekly_revision_time_min": user_input['revision'],
        "distracting_app_count": user_input['distractions'],
        "daily_youtube_edu_min": user_input['edu_youtube'],
        "academic_goal": 1 if user_input['goal'].lower() == 'yes' else 0
    }


def generate_performance_tips(performance, user_input):
    """Generate targeted tips focusing on weak areas"""
    tips = []

    if user_input['attendance'] < 60:
        tips.append(f"🚨 Critical: Your {user_input['attendance']}% attendance is too low - aim for at least 80%")
    elif user_input['attendance'] < 75:
        tips.append(f"🏫 Increase class attendance from {user_input['attendance']}% to 80%+ for better understanding")

    if user_input['sleep'] < 5:
        tips.append(f"😴 Emergency: Increase sleep from {user_input['sleep']} hours to at least 6 (7-8 ideal)")
    elif user_input['sleep'] < 6:
        tips.append(f"🛌 Low sleep ({user_input['sleep']} hours) affects memory - aim for 7-8 hours")

    study_ratio = user_input['study_time'] / user_input['screen_time'] if user_input['screen_time'] > 0 else 1
    if study_ratio < 0.5:
        tips.append(f"📊 Your study:screen ratio is 1:{round(1/study_ratio, 1)} - aim for at least 1:1 balance")

    if performance == 'Poor':
        if user_input['study_time'] < 120:
            tips.append(f"⏰ Double study time from {user_input['study_time']}min to at least 2 hours daily")
        if user_input['distractions'] > 5:
            tips.append(f"📵 Delete {user_input['distractions'] - 2} apps - keep only 2 essential ones")

    elif performance == 'Average':
        if user_input['study_time'] < 150:
            tips.append(f"📖 Increase study time by {150 - user_input['study_time']} minutes to reach 2.5 hours")
        if user_input['revision'] < 180:
            tips.append(f"🔁 Add {180 - user_input['revision']} minutes of weekly revision")

    else:  # Good
        if user_input['attendance'] > 85 && user_input['Weekly physical play minutes'] > 250 :
            tips.append("🎯 Maintain 75% attendance consistently to stay on top")
        if user_input['edu_youtube'] / user_input['screen_time'] < 0.3:
            tips.append("🧠 Increase educational content to 30%+ of screen time for maximum benefit")

    # Add universal tips if space available
    universal_tips = [
        "📅 Plan your week every Sunday night",
        "🔄 Review notes within 24 hours of class",
        "💧 Stay hydrated - even mild dehydration reduces focus",
        "☕ Limit caffeine after 2PM for better sleep quality"
    ]

    if len(tips) < 4:
        tips.extend(universal_tips[:4 - len(tips)])

    return tips[:5]


if __name__ == '__main__':
    app.run(debug=True, port=5000)
