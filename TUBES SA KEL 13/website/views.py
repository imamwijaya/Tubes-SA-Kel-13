from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Note
from . import db
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        workers = int(request.form.get('workers'))
        profit = int(request.form.get('profit'))

        if not project_name or workers <= 0 or profit <= 0:
            flash('Invalid input!', category='error')
        else:
            new_note = Note(project_name=project_name, workers=workers, profit=profit, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Project added!', category='success')

    return render_template('home.html', user=current_user)

def knapsack_bruteforce(items, capacity):
    n = len(items)
    max_profit = 0
    best_combination = []
    
    for i in range(1 << n):
        combination = []
        total_weight = 0
        total_profit = 0
        
        for j in range(n):
            if i & (1 << j):
                total_weight += items[j][1]  # Changed index to 1 for workers
                total_profit += items[j][2]  # Changed index to 2 for profit
                combination.append(items[j])
        
        if total_weight <= capacity and total_profit > max_profit:
            max_profit = total_profit
            best_combination = combination
    
    return max_profit, best_combination  # Changed to return the entire combination

def knapsack_greedy(items, capacity):
    items = sorted(items, key=lambda x: x[2], reverse=True)  # Sort by profit in descending order
    total_weight = 0
    total_profit = 0
    chosen_items = []

    for item in items:
        if total_weight + item[1] <= capacity:  # Changed index to 1 for workers
            total_weight += item[1]  # Changed index to 1 for workers
            total_profit += item[2]  # Changed index to 2 for profit
            chosen_items.append(item)
    
    return total_profit, chosen_items  # Changed to return the entire combination

@views.route('/search', methods=['POST'])
@login_required
def search():
    worker_limit = int(request.form.get('worker_limit'))
    projects = Note.query.filter(Note.user_id == current_user.id).all()
    
    # Filter projects that do not exceed the worker limit
    filtered_projects = [(project.project_name, project.workers, project.profit) for project in projects if project.workers <= worker_limit]

    max_profit_bruteforce, best_combination_bruteforce = knapsack_bruteforce(filtered_projects, worker_limit)
    max_profit_greedy, best_combination_greedy = knapsack_greedy(filtered_projects, worker_limit)

    # Prepare the best combinations with project name, workers, and profit
    best_combination_bruteforce_details = [(project[0], project[1], project[2]) for project in best_combination_bruteforce]
    best_combination_greedy_details = [(project[0], project[1], project[2]) for project in best_combination_greedy]

    return render_template('results.html', 
                           user=current_user, 
                           max_profit_bruteforce=max_profit_bruteforce, 
                           best_combination_bruteforce=best_combination_bruteforce_details, 
                           max_profit_greedy=max_profit_greedy, 
                           best_combination_greedy=best_combination_greedy_details)

@views.route('/delete_notes', methods=['POST'])
@login_required
def delete_notes():
    try:
        # Delete all notes associated with the current user
        Note.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('All projects deleted successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting projects.', category='error')
    return redirect(url_for('views.home'))
