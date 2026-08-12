from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from accounts.models.accounts import TeamAccount, TournamentAccount
from stores.models.inventories import Inventory
from tournaments.models import Tournament
from users.models import User

from .models import Team

# ---------------------- #
# Team Custom Admin Form #
# ---------------------- #

# Admin form that allows for advance team handling
# and updating.
#
# Per each tournament added, team specific accounts get created
# for balance tracking.


class TeamAdminForm(forms.ModelForm):
    """
    Form that makes it manageable to add multiple tournaments,
    and multiple members within a team.

    ----

    Also ensures convenient deletion from both fields.

    ----

    **Contains** the settings:

    - ``members``: The team's members
    - ``tournaments``: The tournaments that the team participates in
    - ``team_account``: The main team account
    - ``create_new_points_account``: Whether to create new points account
    - ``create_new_coins_account``: Whether to create new coins account
    - ``create_new_team_account``: Whether to create new teams account
    """

    members = forms.ModelMultipleChoiceField(
        User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("members", False),
    )

    tournaments = forms.ModelMultipleChoiceField(
        Tournament.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("tournaments", False),
    )

    # -------------- #
    # Data selection #
    # -------------- #

    inventories = forms.ModelMultipleChoiceField(
        Inventory.objects.filter(team=None),
        required=False,
        widget=FilteredSelectMultiple("inventories", False),
    )

    point_accounts = forms.ModelMultipleChoiceField(
        TournamentAccount.objects.points().filter(team=None),
        required=False,
        widget=FilteredSelectMultiple("tournament_accounts", False),
    )

    coin_accounts = forms.ModelMultipleChoiceField(
        TournamentAccount.objects.coins().filter(team=None),
        required=False,
        widget=FilteredSelectMultiple("tournament_accounts", False),
    )

    team_account = forms.ModelChoiceField(TeamAccount.objects.filter(team=None), required=False)

    # ----------------- #
    # Creation Requests #
    # ----------------- #

    create_new_inventories = forms.BooleanField(required=False, initial=True)

    create_new_points_account = forms.BooleanField(required=False, initial=True)

    create_new_coins_account = forms.BooleanField(required=False, initial=True)

    create_new_team_account = forms.BooleanField(required=False, initial=True)

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __init__(self, *args, **kwargs):
        """
        Overridden in order to maintain the existing values,
        as it isn't done by default since Account is the model
        that initiates the relationship.

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        # Intatiate the super class
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Try to retrieve previously assigned accounts / inventories
            self.fields["inventories"].initial = Inventory.objects.filter(team=self.instance)
            self.fields["team_account"].initial = TeamAccount.objects.filter(team=self.instance).first()
            self.fields["point_accounts"].initial = TournamentAccount.objects.points().filter(team=self.instance)
            self.fields["coin_accounts"].initial = TournamentAccount.objects.coins().filter(team=self.instance)

            # Prevent admins from assigning accounts / inventories that already
            # belongs to other teams
            self.fields["inventories"].queryset = Inventory.objects.filter(Q(team=None) | Q(team=self.instance))
            self.fields["team_account"].queryset = TeamAccount.objects.filter(Q(team=None) | Q(team=self.instance))
            self.fields["point_accounts"].queryset = TournamentAccount.objects.points().filter(
                Q(team=None) | Q(team=self.instance)
            )
            self.fields["coin_accounts"].queryset = TournamentAccount.objects.coins().filter(
                Q(team=None) | Q(team=self.instance)
            )

    # ----------------------------- #
    # Form Validation Functionality #
    # ----------------------------- #

    def clean_members(self):
        """
        Overrides the base functionality of cleaning members to be called
        when a member that is already added to a team is being added to
        another team.

        When called, it removes said selection.

        ----

        :param: None

        :return: The list of cleaned members
        :rtype: list
        """

        members = self.cleaned_data.get("members")

        # Check if the instance is already created.
        # If so, then include it in the queryset.
        if self.instance:
            teams = Team.objects.filter(members__in=members).exclude(id=self.instance.id)
        else:
            teams = Team.objects.filter(members__in=members)

        # Check if there are any teams
        if teams.count() > 0:
            # Bundle the error messages if found
            error_message = []

            # Iterate over the given members
            # to check for integrity faults
            for member in members:
                # If the team is not already created
                # exclude it from the search
                if self.instance:
                    member_team = Team.objects.filter(members__in=[member]).exclude(id=self.instance.id)
                else:
                    member_team = Team.objects.filter(members__in=[member])

                # If the member is already part of any
                # other team, throw an error
                if member_team.count() > 0:
                    error_message.append(
                        f"'{member} is also a member of team(s): {', '.join([team.name for team in member_team])}'"
                    )

            # Raise the full error if any faults
            # were found
            if not error_message:
                raise ValidationError(
                    f"The following members are also members of other teams: {', '.join(error_message)}"
                )

        # Return the clean list of members
        return members


# ---------------- #
# Team Admin Panel #
# ---------------- #


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the Team model.

    ----

    **Contains** the settings:

    - ``list_display``: The display field
    - ``search_fields``: The fields that are searchable
    - ``list_filter``: The allowed filters
    """

    list_display = ["name", "total_points", "member_count"]
    search_fields = ("name",)
    list_filter = ("tournaments",)

    # ------------------ #
    # Custom Form Layout #
    # ------------------ #

    form = TeamAdminForm

    # ----------------- #
    # Additional Fields #
    # ----------------- #

    def member_count(self, instance: Team):
        """
        Retrieves the member count of a team.

        ----

        :param instance: The team instance
        :type instance: Team

        :return: The member count
        :rtype: int
        """

        return instance.members.count()

    def tournaments(self, instance: Team):
        """
        List all tournaments that a team belongs to
        in a pretty-printed format.

        ----

        :param instance: The team instance
        :type instance: Team

        :return: The tournaments string list
        :rtype: str
        """

        tournament_list = "\n".join([t.__str__() for t in instance.tournaments.all()])
        return tournament_list

    def total_points(self, instance):
        """
        Retrieve's the team's current total balance

        :param instance: The team instance
        :type instance: Team

        :return: The team balance
        :rtype: int
        """

        return instance.get_main_account().balance

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def save_related(self, request, form, formsets, change):
        """
        Overridden in order to provide utilities when creating a team,
        such as automatic team and inventory retrieval / creations / deletion.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param form: The form
        :type form: admin.ModelForm

        :param formsets: The related forms
        :type formsets: list

        :param change: Whether the object was changed or not
        :type change: bool

        :return: None
        :rtype: None
        """

        super().save_related(request, form, formsets, change)

        self._update_accounts_(form)
        self._update_inventories_(form)

    # ---------------------- #
    # Internal Functionality #
    # ---------------------- #

    def _update_accounts_(self, form):
        """
        Retrieves the accounts from the form and updates them
        respectively, by either deleting old accounts, or creating
        new tournament accounts.

        ----

        :param form: The admin form
        :type form: admin.ModelForm

        :return: None
        :rtype: None
        """

        team = form.instance
        team_account = form.cleaned_data.get("team_account")

        with transaction.atomic():
            # Remove old team accounts to prepare for the new ones
            TeamAccount.objects.filter(team=team).update(team=None)

            # Save the team account if given
            # otherwise create a new one
            create_new_team_account = form.cleaned_data.get("create_new_team_account")
            if team_account:
                team_account.team = team
                team_account.save()
            elif create_new_team_account:
                TeamAccount.objects.create(name=team.name + " total points", team=team)

            point_accounts = form.cleaned_data.get("point_accounts")
            coin_accounts = form.cleaned_data.get("coin_accounts")

            # Remove old tournament accounts to prepare for the new ones
            TournamentAccount.objects.filter(team=team).update(team=None)

            # Save points accounts
            for account in point_accounts:
                account.team = team
                account.save()

            # Save coins accounts
            for account in coin_accounts:
                account.team = team
                account.save()

            create_new_points_account = form.cleaned_data.get("create_new_points_account")
            create_new_coins_account = form.cleaned_data.get("create_new_coins_account")

            selected_point_accounts = {a.tournament for a in point_accounts}
            selected_coin_accounts = {a.tournament for a in coin_accounts}

            # Create new points accounts for tournaments
            if create_new_points_account:
                for t in team.tournaments.all():
                    if t not in selected_point_accounts:
                        TournamentAccount.objects.create(
                            name=team.name + t.__str__() + " points", team=team, tournament=t, type="points"
                        )

            # Create new coins accounts for tournaments
            if create_new_coins_account:
                for t in team.tournaments.all():
                    if t not in selected_coin_accounts:
                        TournamentAccount.objects.create(
                            name=team.name + t.__str__() + " coins", team=team, tournament=t, type="coins"
                        )

    def _update_inventories_(self, form):
        """
        Retrieves the inventories from the form and updates them
        respectively, by either deleting old inventories, or creating
        new ones.

        ----

        :param form: The admin form
        :type form: admin.ModelForm

        :return: None
        :rtype: None
        """

        team_inventories = form.cleaned_data.get("inventories")
        team = form.instance

        Inventory.objects.filter(team=team).exclude(id__in=[i.id for i in team_inventories]).update(team=None)

        for inventory in team_inventories:
            inventory.team = team
            inventory.save()

        # Delete all the inventories that belong to tournaments that are
        # no longer in use
        active_tournaments = set(team.tournaments.all())
        Inventory.objects.filter(team=team).exclude(tournament__in=active_tournaments).delete()

        if form.cleaned_data.get("create_new_inventories"):
            # Retrieve all existing inventories for the given
            # tournaments
            existing_inventory_tournaments = set(
                Inventory.objects.filter(team=team, tournament__isnull=False).values_list("tournament_id", flat=True)
            )

            # Create new inventories for newly added tournaments
            for tournament in active_tournaments:
                if tournament.id not in existing_inventory_tournaments:
                    Inventory.objects.create(team=team, tournament=tournament)
