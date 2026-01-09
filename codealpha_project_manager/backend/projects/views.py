from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Project, Column, Task, Comment


@login_required
def dashboard(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            project = Project.objects.create(name=name)
            project.members.add(request.user)

            Column.objects.bulk_create([
                Column(project=project, name="To Do", order=1),
                Column(project=project, name="Doing", order=2),
                Column(project=project, name="Done", order=3),
            ])

    projects = Project.objects.filter(members=request.user)
    return render(request, "projects/dashboard.html", {
        "projects": projects
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Security check
    if request.user not in project.members.all():
        return redirect('dashboard')

    action = None

    if request.method == "POST":
        action = request.POST.get("action")

        # ADD TASK
        if action == "add_task":
            column_id = request.POST.get("column")
            title = request.POST.get("title")
            if title:
                column = Column.objects.get(id=column_id)
                Task.objects.create(column=column, title=title)

        # ADD COMMENT
        elif action == "comment":
            task_id = request.POST.get("task_id")
            text = request.POST.get("comment")
            if text:
                task = Task.objects.get(id=task_id)
                Comment.objects.create(task=task, user=request.user, text=text)

        # ASSIGN TASK
        elif action == "assign":
            task = Task.objects.get(id=request.POST.get("task_id"))
            user = User.objects.get(id=request.POST.get("assigned_to"))
            task.assigned_to = user
            task.save()

        # INVITE MEMBER
        elif action == "invite":
            username = request.POST.get("username")
            try:
                user = User.objects.get(username=username)
                project.members.add(user)
            except User.DoesNotExist:
                pass

    columns = project.columns.all().order_by("order")

    return render(request, "projects/project_detail.html", {
        "project": project,
        "columns": columns,
    })
