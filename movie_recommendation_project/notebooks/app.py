from shiny import App, ui, render, reactive
### W.I.P converting App to Shiny

app_ui = ui.page_fillable(
        ui.navset_bar(
            ui.nav_panel("Home",
                ui.layout_column_wrap(
                    ui.card(
                        ui.input_text("movies", "Movies Input", placeholder= "Enter Favorite Movies..."),
                        ui.input_task_button("action_button", "Submit",),
                        ui.output_text("movie_names")
                    ),
                    ui.card(

                    ),
                    width = 1/2
                )
            ), id = "selected_navset_bar", title = ui.HTML("<h1><b>Movie Rec System</b></h1>")
        )
, theme = ui.Theme(preset = "superhero")
)


def server(input, output, session):
    @output
    @render.text()
    @reactive.event(input.action_button)
    def movie_names():
        x = input.movies()
        x_cleaned = x.split(" ")
        return f"You entered: {", ".join(x_cleaned)}"
    
app = App(app_ui, server)