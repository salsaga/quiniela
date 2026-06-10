// Posiciona la vista por día en los partidos de hoy. Si hoy no hay
// partidos, cae al primer día futuro (los días pasados quedan arriba,
// alcanzables scrolleando hacia arriba).
document.addEventListener("DOMContentLoaded", () => {
    const target =
        document.querySelector(".day[data-today]") ||
        document.querySelector(".day[data-future]");
    target?.scrollIntoView({ block: "start" });
});
