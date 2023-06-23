import pickle

from cases.sensitivity_analysis.configuration_sa import sa_surrogate_estimator
from cases.breakwaters.configuration_de import bw_domain
from cases.sensitivity_analysis.creator_structures import get_structure
from cases.main_conf import opt_params

domain, task_setup = bw_domain.configurate_domain(
    poly_num=opt_params.n_polys,
    points_num=opt_params.n_points,
    is_closed=opt_params.is_closed,
)

estimator = sa_surrogate_estimator.configurate_estimator(domain=domain)


if __name__ == "__main__":
    number_experiments = 30
    evo_steps = 80
    pop_size = 15
    for i in range(number_experiments):
        full_archive = {}

        step_for_start_sa = [0.25, 0.5, 0.75, 1]
        step_for_start_sa = [
            round(evo_steps * percent_step) - 1 for percent_step in step_for_start_sa
        ]
        best_evo_structure = get_structure(n_steps=evo_steps, pop_size=pop_size)

        with open(f"HistoryFiles/time_history.pickle", "rb") as f:
            evo_time_history = pickle.load(f)
            f.close()
        full_archive["evo_time_history"] = evo_time_history

        evo_fitnes_history = []
        for step in range(evo_steps):
            with open(f"HistoryFiles/performance_{step}.pickle", "rb") as f:
                step_fit = pickle.load(f)
                evo_fitnes_history.append(step_fit[0])
                f.close()
        full_archive["evo_fitnes_history"] = evo_fitnes_history

        for step_start in step_for_start_sa:
            step_archive = {}
            with open(f"HistoryFiles/population_{step_start}.pickle", "rb") as f:
                population_for_start_sa = pickle.load(f)
                f.close()
            optimized_pop = population_for_start_sa[0]
            step_archive[f"initial_structure_{step_start}"] = optimized_pop

            sensitivity = SA()
            fitnes, structure, poly = sensitivity.analysis()

            sa_time_history = sensitivity.get_time_history
            sa_time_history = [
                time_sa + evo_time_history[step_start - 1]
                for time_sa in sa_time_history
            ]
            step_archive[f"sa_fitnes_{step_start}"] = fitnes
            step_archive[f"sa_structures_{step_start}"] = structure
            step_archive[f"sa_step_description_{step_start}"] = poly
            step_archive[f"sa_time_{step_start}"] = sa_time_history

            full_archive[f"sa_step_{step_start}"] = step_archive

        with open(f"HistorySA/sa_archive_{i}.pickle", "wb") as handle:
            pickle.dump(full_archive, handle, protocol=pickle.HIGHEST_PROTOCOL)
