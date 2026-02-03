import { createRouter, createWebHistory } from "vue-router";
import MainContentView from "../views/MainContentView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: MainContentView,
    },
    {
      path: "/detalhes/:cnpj",
      name: "detalhes",
      component: () => import("../views/DetailsView.vue"),
    },
  ],
});

export default router;
