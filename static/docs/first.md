# Project Progress Report: Calisthenics App

## Overview

This document outlines the development progress of the Calisthenics App, detailing the journey from a collection of static HTML templates to a foundational, dynamic web application powered by Flask and a database backend. The "Workouts" feature has been fully implemented as a proof-of-concept for this dynamic architecture.

## Key Technologies Used

-   **Backend:** Python, Flask
-   **Database:** SQLAlchemy, Flask-Migrate, SQLite
-   **Frontend:** HTML, CSS, JavaScript
-   **Templating:** Jinja2

---

## Phase 1: Initial Setup & Static Serving

The project began with a well-defined file structure containing static HTML, CSS, and image assets. The initial goal was to serve these static files via a web server.

-   **Flask Application Created (`app.py`):** A basic Flask server was established.
-   **Static Route Mapping:** A unique route was created for each of the 11 HTML templates (`/`, `/dashboard`, `/workouts`, etc.), allowing each page to be viewed in the browser.
-   **Virtual Environment:** All work was conducted within a properly configured virtual environment.

## Phase 2: Code Refactoring & Organization

The focus of this phase was to improve code quality, maintainability, and adhere to web development best practices.

-   **CSS Externalization:** The inline `<style>` block from `index.html` was extracted into a dedicated stylesheet at `static/css/index.css`. This separates presentation from structure.
-   **Multi-Page Application Conversion:** The single-page, JavaScript-driven navigation in `index.html` was refactored:
    -   Sidebar links were updated from `href="#"` to use Jinja's `{{ url_for(...) }}` to point to the backend routes.
    -   Redundant HTML content for other pages was removed from `index.html`.
    -   The page-switching JavaScript was removed, establishing a true multi-page navigation flow.
-   **Componentization with `_sidebar.html`:** The sidebar navigation was extracted from `index.html` into a reusable partial template, `_sidebar.html`. All pages now include this component using `{% include '_sidebar.html' %}`, ensuring consistency and easy updates.
-   **Dynamic Active Link:** The sidebar was enhanced to dynamically apply an `active` class based on the current page, providing clear visual feedback to the user.

## Phase 3: Transition to a Dynamic, Database-Driven Application

This was the most critical phase, converting the static "Workouts" page into a fully dynamic feature connected to a database.

### 3.1. Database Integration

-   **Frameworks:** `Flask-SQLAlchemy` and `Flask-Migrate` were integrated into `app.py`.
-   **Database Model:** A `Workout` model was defined in Python, creating a blueprint for the `workouts` table with columns for `id`, `name`, `difficulty`, `sets`, `reps`, `rest`, and `instructions`.
-   **Schema Creation:** `flask db` commands were used to initialize the migration environment, generate the table schema, and apply it, creating the `calisthenics.db` database file.

### 3.2. Data Seeding

-   **`seed.py` Script:** A standalone script was created to populate the empty database with the six initial workouts that were previously hardcoded in the HTML. This ensured the application had data to display immediately.

### 3.3. Dynamic Content Rendering

-   **Backend Logic:** The `/workouts` route was updated to query the database (`Workout.query.all()`) and fetch all workout records.
-   **Frontend Templating:** The `Workouts.html` template was completely refactored. The hardcoded exercise cards were replaced with a single card inside a Jinja `{% for workout in workouts %}` loop. All static text and values were replaced with dynamic variables (e.g., `{{ workout.name }}`, `{{ workout.difficulty }}`).

## Phase 4: Implementing Core Application Features (CRUD)

Building on the dynamic foundation, we implemented Create, Read, and Delete functionalities for workouts.

-   **Create (Add Workout):**
    -   A new `/workouts/add` route was created to handle `POST` requests.
    -   An HTML modal (pop-up form) was added to `Workouts.html`.
    -   JavaScript was implemented to control the modal's visibility.
    -   The form submits data to the backend, which validates it, creates a new `Workout` record, and saves it to the database.
-   **Read (View Workouts):** This was achieved in Phase 3 and is the primary view of the `/workouts` page.
-   **Delete (Remove Workout):**
    -   A new `/workouts/delete/<int:workout_id>` route was created.
    -   The delete button on each card was converted into a small form that securely submits a `POST` request to this route.
    -   The backend removes the specified record from the database.
-   **User Feedback:** Flask's `flash()` messaging system was implemented to provide success or error alerts to the user after adding or deleting a workout.

---

## Current Project Status

-   **Workouts Page:** Fully dynamic and persistent. Users can view, add, and delete workouts. All changes are saved to the database.
-   **Other Pages:** Currently served as static placeholders but are integrated with the shared, dynamic sidebar.
-   **Codebase:** Well-organized, with a clear separation of concerns (Python backend, HTML templates, CSS stylesheets, and client-side JS). The structure is now scalable and ready for other features to be converted to a dynamic model.
