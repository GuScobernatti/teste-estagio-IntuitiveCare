<script setup>
import { onMounted, ref, onUpdated } from "vue";
import { useRouter } from "vue-router";
import {
  Search,
  BarChart3,
  Eye,
  ChevronLeft,
  ChevronRight,
  Trophy,
} from "lucide-vue-next";
import Chart from "chart.js/auto";

const router = useRouter();

const API_URL = import.meta.env.VITE_API_URL;

const operatorsData = ref(null);
const statisticsData = ref(null);
const currentPage = ref(1);
const searchQuery = ref("");
const chartCanvas = ref(null);
const isTableLoading = ref(false);

const loadOperators = async (page) => {
  isTableLoading.value = true;

  try {
    const fetchOperators = await fetch(
      `${API_URL}/api/operadoras?page=${page}&limit=10${searchQuery.value ? `&query_search=${searchQuery.value}` : ""}`,
    );
    const operatorsJSON = await fetchOperators.json();
    operatorsData.value = operatorsJSON;
    currentPage.value = page;
  } catch (err) {
    console.error("Erro ao carregar dados:", err);
    operatorsData.value = { operators: [], total: 0, page: 1, total_pages: 1 };
  } finally {
    isTableLoading.value = false;
  }
};

const loadStatistics = async () => {
  try {
    const fetchStatistics = await fetch(`${API_URL}/api/estatisticas`);
    const statisticsJSON = await fetchStatistics.json();
    statisticsData.value = statisticsJSON;
    await createChart();
  } catch (err) {
    console.error("Erro ao carregar estatisticas:", err);
    operatorsData.value = {
      total_geral: 0,
      media_geral: 0,
      top_5_operadoras: [],
      distribuicao_uf: [],
    };
  }
};

let chartInstance = null;
const createChart = async () => {
  if (!chartCanvas.value) return;

  const data = await statisticsData.value;

  if (!data || !data.distribuicao_uf || data.distribuicao_uf.length === 0)
    return;

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels: data.distribuicao_uf.map((row) => row.uf),
      datasets: [
        {
          label: "Distribuição de despesas por UF",
          data: data.distribuicao_uf.map((row) => row.despesas),
          backgroundColor: "#3b82f6",
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              if (label) {
                label += ": ";
              }
              if (context.parsed.y !== null) {
                label += new Intl.NumberFormat("pt-BR", {
                  style: "currency",
                  currency: "BRL",
                }).format(context.parsed.y);
              }
              return label;
            },
          },
        },
      },
      scales: {
        y: {
          ticks: {
            callback: function (value) {
              return new Intl.NumberFormat("pt-BR", {
                notation: "compact",
                compactDisplay: "short",
                style: "currency",
                currency: "BRL",
              }).format(value);
            },
          },
        },
      },
    },
  });
};

onMounted(() => {
  loadOperators(1);
  loadStatistics();
});

onUpdated(() => {
  if (!chartInstance && statisticsData.value) createChart();
});

const changePage = (newPage) => {
  loadOperators(newPage);
};

const details = (cnpj) => {
  router.push(`/detalhes/${cnpj}`);
};
</script>

<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <h1>Monitoramento de Operadoras</h1>
      <p class="subtitle">Visão geral de despesas e cadastro ANS</p>
    </header>

    <div v-if="!operatorsData" class="loading-overlay">
      <div class="spinner"></div>
      <p>Carregando dados do sistema...</p>
    </div>

    <main v-else class="dashboard-content fade-in">
      <div class="stats-grid">
        <section class="chart-card">
          <div class="card-header">
            <h3><BarChart3 :size="20" /> Distribuição de Despesas por UF</h3>
          </div>
          <div class="chart-wrapper">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </section>

        <section class="top5-card" v-if="statisticsData">
          <div class="card-header">
            <h3>
              <Trophy :size="20" color="#eab308" /> Top 5 maiores despesas
            </h3>
          </div>
          <div class="top5-list">
            <div
              v-for="(op, index) in statisticsData.top_5_operadoras"
              :key="op.registro_ans"
              class="top5-item"
            >
              <div class="rank-circle">{{ index + 1 }}</div>
              <div class="op-info">
                <span class="op-name" :title="op.razao_social">
                  {{ op.razao_social }}
                </span>
                <span class="op-value">
                  {{
                    Number(op.total).toLocaleString("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    })
                  }}
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section class="controls-section">
        <div class="search-box">
          <Search class="search-icon" :size="20" color="#64748b" />
          <input
            type="text"
            v-model="searchQuery"
            v-on:change="loadOperators(1)"
            placeholder="Razão Social ou CNPJ"
          />
        </div>
        <button class="btn-search" v-on:click="loadOperators(1)">
          Pesquisar
        </button>
      </section>

      <div
        v-if="operatorsData && operatorsData.operators.length === 0"
        class="no-results"
      >
        <h3>Nenhum registro encontrado</h3>
        <p>Nenhuma operadora encontrada com esse termo.</p>
      </div>

      <section
        v-else
        class="table-card"
        :class="{ 'loading-opacity': isTableLoading }"
      >
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Registro ANS</th>
                <th>CNPJ</th>
                <th>Razão Social</th>
                <th>UF</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-if="operatorsData"
                v-for="op in operatorsData.operators"
                :key="op.registro_ans"
              >
                <td>{{ op.registro_ans }}</td>
                <td>{{ op.cnpj }}</td>
                <td>
                  <strong>{{ op.razao_social }}</strong>
                </td>
                <td>
                  <span class="badge-uf">{{ op.uf }}</span>
                </td>
                <td>
                  <button class="btn-details" v-on:click="details(op.cnpj)">
                    <Eye :size="16" /> Ver Detalhes
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-controls" v-if="operatorsData">
          <span class="page-info">
            Página <strong>{{ operatorsData.page }}</strong> de
            <strong>{{ operatorsData.total_pages }}</strong>
          </span>
          <div class="buttons">
            <button
              :disabled="operatorsData.page === 1"
              v-on:click="changePage(operatorsData.page - 1)"
            >
              Anterior
            </button>
            <button
              :disabled="operatorsData.page === operatorsData.total_pages"
              v-on:click="changePage(operatorsData.page + 1)"
            >
              Próximo
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.loading-opacity {
  opacity: 0.5;
  pointer-events: none;
  transition: opacity 0.3s;
}
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: "Inter", sans-serif;
  color: #2c3e50;
}

.dashboard-header {
  margin-bottom: 2rem;
}
.dashboard-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
.subtitle {
  color: #64748b;
  font-size: 0.9rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: stretch;
}

.top5-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  overflow-y: auto;
}

.top5-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.top5-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.top5-item:last-child {
  border-bottom: none;
}

.rank-circle {
  width: 28px;
  height: 28px;
  background-color: #eff6ff;
  color: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.op-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.op-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.op-value {
  font-size: 0.85rem;
  color: red;
  font-weight: 500;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #64748b;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e2e8f0;
  border-top: 5px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
  gap: 1rem;
}

.chart-card,
.table-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: white;
  flex-shrink: 0;
}
.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #0f172a;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.chart-wrapper {
  padding: 1rem;
  height: 350px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder-text {
  color: #94a3b8;
  text-align: center;
}

.controls-section {
  display: flex;
  gap: 10px;
  margin-bottom: 1.5rem;
}
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 500px;
  max-width: 400px;
}
.search-icon {
  position: absolute;
  left: 12px;
  opacity: 0.5;
}
.search-box input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}
.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.btn-search {
  background-color: #3b82f6;
  border: none;
  padding: 0 12px;
  border-radius: 8px;
  cursor: pointer;
  max-width: 400px;
  color: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transition: all 0.5s;
}
.btn-search:hover {
  background-color: #0d51be;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 1rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #e2e8f0;
}

tbody td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.95rem;
  color: #334155;
}

tbody tr:last-child td {
  border-bottom: none;
}

tbody tr:hover {
  background-color: #f8fafc;
}

.badge-uf {
  background-color: #dbeafe;
  color: #1e40af;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.8rem;
}

.btn-details {
  background-color: transparent;
  border: 1px solid #e2e8f0;
  color: #3b82f6;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-details:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.pagination-controls button {
  padding: 8px 16px;
  border: 1px solid #cbd5e1;
  background-color: white;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 8px;
  color: #334155;
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f1f5f9;
}

.pagination-controls button:not(:disabled):hover {
  border-color: #94a3b8;
  background-color: #f1f5f9;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .chart-wrapper,
  .top5-list {
    height: 300px;
  }

  .search-box {
    max-width: 100%;
  }

  .pagination-controls {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
