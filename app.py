"""
CareerBridge — Course & Internship Finding Platform
Version 3: Clean rewrite using standard Streamlit components only.

Run with:  streamlit run app.py
"""

import streamlit as st
from datetime import datetime

from data import LISTINGS, ALL_DOMAINS
from recommender import recommend, build_app_counts
from storage import (
    get_user, save_user,
    get_profile, save_profile, save_resume, get_resume_path,
    load_applications, already_applied, apply, update_status,
    load_provider_listings, save_listing,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerBridge",
    page_icon="🎓",
    layout="wide",
)

# ── Session state defaults ─────────────────────────────────────────────────────
for key, default in {
    "logged_in": False,
    "username":  None,
    "role":      None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def all_listings() -> list:
    """Merge hardcoded sample listings with provider-posted ones."""
    return LISTINGS + load_provider_listings()


def show_listing_card(listing: dict, applied_ids: set):
    """
    Display one listing using standard Streamlit components.
    Shows an Apply button and handles duplicate prevention.
    """
    lid  = listing["id"]
    paid = "💰 Paid" if listing["paid"] else "🆓 Free"
    ltype = "📚 Course" if listing["type"] == "Course" else "💼 Internship"

    with st.container(border=True):
        col_info, col_action = st.columns([4, 1])

        with col_info:
            st.subheader(listing["title"])
            st.caption(f"{ltype}  ·  {paid}  ·  🏢 {listing['provider']}  ·  ⏱ {listing['duration']}  ·  🏷 {listing['domain']}")
            st.write(listing["description"])

        with col_action:
            st.write("")  # vertical spacing
            if lid in applied_ids:
                st.success("✅ Applied")
            else:
                if st.button("Apply", key=f"apply_{lid}", use_container_width=True):
                    apply(st.session_state.username, lid, listing["title"])
                    st.success("Applied!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

def page_auth():
    st.title("🎓 CareerBridge")
    st.caption("Find courses and internships matched to your skills.")
    st.divider()

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        st.subheader("Login")
        username = st.text_input("Username", key="li_user")
        password = st.text_input("Password", type="password", key="li_pass")

        if st.button("Login", key="li_btn"):
            if not username or not password:
                st.warning("Please fill in both fields.")
                return
            user = get_user(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.role      = user["role"]
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    with tab_signup:
        st.subheader("Create Account")
        new_user = st.text_input("Choose a username", key="su_user")
        new_pass = st.text_input("Choose a password", type="password", key="su_pass")
        role     = st.selectbox("I am a", ["Student", "Provider"], key="su_role")

        if st.button("Sign Up", key="su_btn"):
            if not new_user or not new_pass:
                st.warning("Please fill in all fields.")
                return
            if get_user(new_user):
                st.error("That username is already taken.")
                return
            save_user(new_user, new_pass, role.lower())
            st.success("Account created! You can now log in.")


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT PAGES
# ══════════════════════════════════════════════════════════════════════════════

def page_browse():
    st.header("Browse Listings")

    # ── Filters ──
    col1, col2, col3 = st.columns(3)
    with col1:
        keyword = st.text_input("Search by keyword", placeholder="e.g. Python, Design")
    with col2:
        domain_choice = st.selectbox("Filter by domain", ["All"] + ALL_DOMAINS)
    with col3:
        type_choice = st.selectbox("Filter by type", ["All", "Course", "Internship"])

    listings = all_listings()

    # Apply filters
    if keyword:
        kw = keyword.lower()
        listings = [
            l for l in listings
            if kw in l["title"].lower()
            or kw in l["description"].lower()
            or kw in l["domain"].lower()
        ]
    if domain_choice != "All":
        listings = [l for l in listings if l["domain"] == domain_choice]
    if type_choice != "All":
        listings = [l for l in listings if l["type"] == type_choice]

    st.write(f"Showing **{len(listings)}** listing(s)")
    st.divider()

    if not listings:
        st.info("No listings match your filters. Try a different keyword or domain.")
        return

    # Fetch applied IDs once so we don't re-read the file per card
    apps        = load_applications()
    applied_ids = {a["listing_id"] for a in apps if a["student"] == st.session_state.username}

    for listing in listings:
        show_listing_card(listing, applied_ids)


def page_recommendations():
    st.header("🤖 AI Recommendations")
    st.write("Scored across title relevance, domain match, description depth, and listing popularity.")

    profile      = get_profile(st.session_state.username)
    saved_skills = profile.get("skills", "")

    if saved_skills:
        st.info(f"Skills from your profile: **{saved_skills}** — edit below to override.")

    skills_input = st.text_input(
        "Your skills (comma-separated)",
        value=saved_skills,
        placeholder="e.g. Python, Machine Learning, React",
    )

    if st.button("Get Recommendations"):
        skills = [s.strip() for s in skills_input.split(",") if s.strip()]
        if not skills:
            st.warning("Please enter at least one skill.")
            return

        # Build popularity counts from real application history
        app_counts = build_app_counts(load_applications())
        results    = recommend(skills, all_listings(), application_counts=app_counts)

        if not results:
            st.info("No matches found. Try broader terms like 'Python' or 'Design'.")
            return

        apps        = load_applications()
        applied_ids = {a["listing_id"] for a in apps if a["student"] == st.session_state.username}

        st.success(f"Found {len(results)} recommendation(s) — ranked by relevance score.")
        st.divider()

        for result in results:
            listing       = result["listing"]
            score         = result["final_score"]
            matched       = result["matched_skills"]
            signals       = result["signal_scores"]

            # Score bar: fill based on percentage
            bar_filled = "█" * (score // 10)
            bar_empty  = "░" * (10 - score // 10)

            col_score, col_detail = st.columns([1, 5])
            with col_score:
                st.metric("Score", f"{score}/100")
                st.caption(f"{bar_filled}{bar_empty}")
            with col_detail:
                show_listing_card(listing, applied_ids)
                if matched:
                    st.caption(f"Matched skills: **{', '.join(matched)}**")
                with st.expander("Signal breakdown", expanded=False):
                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("Title",       f"{signals['title']}%")
                    s2.metric("Domain",      f"{signals['domain']}%")
                    s3.metric("Description", f"{signals['description']}%")
                    s4.metric("Popularity",  f"{signals['popularity']}%")
            st.divider()

    with st.expander("How does the scoring work?"):
        st.write("""
**Four weighted signals combine into a final score out of 100:**

| Signal | Weight | What it measures |
|---|---|---|
| Title match | 40% | Skill appears in the listing title |
| Domain match | 30% | Skill aligns with the listing's domain |
| Description match | 20% | Skill appears in the full description |
| Popularity boost | 10% | Listings more students applied to rank higher |

**Why weights matter:** A skill in a listing's title is a much stronger relevance
signal than one buried in the description. This mirrors how real recommendation
systems (YouTube, Netflix) weight different engagement signals differently.

**Upgrade path to ML:**
- Stage 1 — TF-IDF + Cosine Similarity: handles synonyms, no training needed
- Stage 2 — Sentence Transformers: semantic matching ("Flask" → "Web Dev")
- Stage 3 — Collaborative Filtering: "students like you applied to..."
        """)


def page_my_applications():
    st.header("My Applications")

    apps = [a for a in load_applications() if a["student"] == st.session_state.username]

    if not apps:
        st.info("You haven't applied to anything yet. Go to Browse or Recommendations to get started!")
        return

    # Summary counts
    counts = {"applied": 0, "selected": 0, "rejected": 0, "enrolled": 0}
    for a in apps:
        counts[a["status"]] = counts.get(a["status"], 0) + 1

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total",    len(apps))
    col2.metric("Selected", counts["selected"])
    col3.metric("Pending",  counts["applied"])
    col4.metric("Enrolled", counts["enrolled"])

    st.divider()

    # Status badge mapping
    icons = {
        "applied":  "🟡 Applied",
        "selected": "🟢 Selected",
        "rejected": "🔴 Rejected",
        "enrolled": "🔵 Enrolled",
    }

    for a in sorted(apps, key=lambda x: x["applied_on"], reverse=True):
        with st.container(border=True):
            col_text, col_status = st.columns([4, 1])
            with col_text:
                st.write(f"**{a['listing_title']}**")
                st.caption(f"Applied on: {a['applied_on']}")
            with col_status:
                st.write(icons.get(a["status"], a["status"]))


def page_profile():
    st.header("My Profile")

    profile  = get_profile(st.session_state.username)
    username = st.session_state.username

    # ── Current resume ──
    st.subheader("Resume")
    resume_fn = profile.get("resume_filename", "")
    if resume_fn:
        st.write(f"Current file: **{resume_fn}**")
        resume_path = get_resume_path(resume_fn)
        if resume_path:
            with open(resume_path, "rb") as f:
                st.download_button(
                    "Download my resume",
                    data=f.read(),
                    file_name=resume_fn,
                    mime="application/pdf",
                )
    else:
        st.write("No resume uploaded yet.")

    st.divider()

    # ── Edit form ──
    st.subheader("Edit Profile")
    with st.form("profile_form"):
        name   = st.text_input("Full name",   value=profile.get("name", ""),   placeholder="e.g. Priya Sharma")
        skills = st.text_input("Your skills (comma-separated)",
                               value=profile.get("skills", ""),
                               placeholder="Python, Machine Learning, React")
        resume_file = st.file_uploader("Upload / replace resume (PDF only)", type=["pdf"])
        submitted   = st.form_submit_button("Save Profile")

    if submitted:
        new_resume_fn = ""
        if resume_file is not None:
            new_resume_fn = save_resume(username, resume_file.name, resume_file.read())
        save_profile(username, name, skills, new_resume_fn)
        st.success("Profile saved!")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PROVIDER PAGES
# ══════════════════════════════════════════════════════════════════════════════

def page_post_listing():
    st.header("Post a New Listing")

    with st.form("post_form"):
        title       = st.text_input("Title *",       placeholder="e.g. Python for Data Science")
        ltype       = st.selectbox("Type", ["Course", "Internship"])
        domain      = st.selectbox("Domain", ALL_DOMAINS + ["Other"])
        description = st.text_area("Description *",  placeholder="What will students learn or do?", height=120)
        duration    = st.text_input("Duration",       placeholder="e.g. 4 weeks, 3 months")
        paid        = st.checkbox("This is a paid listing")
        submitted   = st.form_submit_button("Publish Listing")

    if submitted:
        if not title.strip() or not description.strip():
            st.error("Title and description are required.")
            return
        listing = {
            "id":          f"p_{st.session_state.username}_{int(datetime.now().timestamp())}",
            "type":        ltype,
            "title":       title.strip(),
            "provider":    st.session_state.username,
            "duration":    duration.strip() or "Flexible",
            "description": description.strip(),
            "domain":      domain,
            "paid":        paid,
        }
        save_listing(listing)
        st.success(f"'{title}' published! Students can now find and apply to it.")


def page_manage_listings():
    st.header("Manage My Listings")

    my_listings = [
        l for l in load_provider_listings()
        if l["provider"] == st.session_state.username
    ]
    all_apps = load_applications()

    if not my_listings:
        st.info("You haven't posted any listings yet.")
        return

    for listing in my_listings:
        apps_for = [a for a in all_apps if a["listing_id"] == listing["id"]]

        with st.expander(f"{listing['title']}  ·  {listing['type']}  ·  {len(apps_for)} applicant(s)"):
            st.write(f"**Duration:** {listing['duration']}")
            st.write(f"**Domain:** {listing['domain']}")
            st.divider()

            if not apps_for:
                st.write("No applications yet.")
                continue

            for app in apps_for:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"👤 **{app['student']}**")
                    st.caption(f"Applied: {app['applied_on']}")
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        ["applied", "selected", "rejected", "enrolled"],
                        index=["applied", "selected", "rejected", "enrolled"].index(app["status"]),
                        key=f"sel_{app['student']}_{listing['id']}",
                    )
                with col3:
                    st.write("")
                    if st.button("Update", key=f"upd_{app['student']}_{listing['id']}"):
                        update_status(app["student"], listing["id"], new_status)
                        st.success("Updated!")
                        st.rerun()

                st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR + MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Not logged in → show auth page
    if not st.session_state.logged_in:
        page_auth()
        return

    username = st.session_state.username
    role     = st.session_state.role

    # ── Sidebar ──
    with st.sidebar:
        st.title("🎓 CareerBridge")
        st.caption("Courses & Internships")
        st.divider()

        profile      = get_profile(username)
        display_name = profile.get("name") or username
        st.write(f"**{display_name}**")
        st.caption(f"@{username}  ·  {role.capitalize()}")
        st.divider()

        if role == "student":
            pages = ["Browse", "Recommendations", "My Applications", "My Profile"]
        else:
            pages = ["Post Listing", "Manage Listings"]

        page = st.radio("Menu", pages, label_visibility="collapsed")

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username  = None
            st.session_state.role      = None
            st.rerun()

    # ── Route to page ──
    if role == "student":
        if page == "Browse":            page_browse()
        elif page == "Recommendations": page_recommendations()
        elif page == "My Applications": page_my_applications()
        elif page == "My Profile":      page_profile()
    else:
        if page == "Post Listing":      page_post_listing()
        elif page == "Manage Listings": page_manage_listings()


if __name__ == "__main__":
    main()