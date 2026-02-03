<script setup>
import { onMounted, onUnmounted, ref, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import Chart from "chart.js/auto";
import { ArrowLeft, Building2, TrendingUp, History } from "lucide-vue-next";

const router = useRouter();
const route = useRoute();

const API_URL = import.meta.env.VITE_API_URL;

const operatorData = ref(null);
const operatorExpensesData = ref(null);
const operatorDataChart = ref(null);
const chartCanvas = ref(null);
const isLoading = ref(true);

const loadOperator = async () => {
  try {
    const fetchOperator = await fetch(
      `${API_URL}/api/operadoras/${route.params.cnpj}`,
    );
    const operatorJSON = await fetchOperator.json();
    operatorData.value = operatorJSON;
  } catch (err) {
    console.error("Erro ao carregar dados da operadora:", err);
    operatorData.value = null;
  }
};

const loadOperatorExpenses = async () => {
  try {
    const fetchOperatorExpenses = await fetch(
      `${API_URL}/api/operadoras/${route.params.cnpj}/despesas`,
    );
    const operatorExpensesJSON = await fetchOperatorExpenses.json();
    operatorExpensesData.value = operatorExpensesJSON;
  } catch (err) {
    console.error("Erro ao carregar dados:", err);
    operatorExpensesData.value = null;
  }
};

const loadDataChart = async () => {
  try {
    const fetchDataChart = await fetch(
      `${API_URL}/api/operadoras/${route.params.cnpj}/despesas/chart`,
    );
    const dataChartJSON = await fetchDataChart.json();
    operatorDataChart.value = dataChartJSON;
  } catch (err) {
    console.error("Erro ao carregar dados:", err);
    operatorDataChart.value = { chart: [] };
  }
};

let chartInstance = null;
const createChart = async () => {
  if (!chartCanvas.value || !operatorDataChart.value) return;

  const data = await operatorDataChart.value;
  if (Array.isArray(data) && data.length === 0) return;

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels: data.chart.map(
        (row) => `${row.ano} / ${formatTrimester(row.trimestre)}`,
      ),
      datasets: [
        {
          label: "Distribuição de despesas por trimestre",
          data: data.chart.map((row) => row.total),
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

onMounted(async () => {
  await Promise.all([loadOperator(), loadOperatorExpenses(), loadDataChart()]);
  isLoading.value = false;
  await nextTick();
  createChart();
});

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy();
});

const formatTrimester = (trimester) => {
  return `${trimester}º Trimestre`;
};

const moneyColor = (value) => {
  return Number(value) <= 0 ? "text-green" : "text-slate";
};

const home = () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
  router.push("/");
};
</script>

<template>
  <div v-if="isLoading" class="loading-overlay">
    <div class="spinner"></div>
    <p>Carregando dados do sistema...</p>
  </div>

  <div v-else class="details-page fade-in">
    <div class="nav-header">
      <button class="btn-back" v-on:click="home()">
        <ArrowLeft :size="20" />
        <span>Voltar</span>
      </button>
    </div>

    <header class="card profile-header">
      <div class="profile-icon"><Building2 :size="32" color="#3b82f6" /></div>
      <div class="profile-info">
        <h1 class="company-name">{{ operatorData[0].razao_social }}</h1>
        <div class="meta-tags">
          <span class="tag">CNPJ: {{ operatorData[0].cnpj }}</span>
          <span class="tag"
            >Registro ANS: {{ operatorData[0].registro_ans }}</span
          >
          <span class="tag uf">{{ operatorData[0].uf }}</span>
        </div>
      </div>
    </header>

    <div
      v-if="operatorExpensesData && operatorExpensesData.length == 0"
      class="no-results"
    >
      <h3>Nenhum registro encontrado</h3>
      <p>
        Esta operadora não possui despesas lançadas nos períodos analisados.
      </p>
    </div>

    <main v-else class="content-grid">
      <section class="card chart-section">
        <div class="card-title">
          <h3><TrendingUp :size="20" />Evolução de Despesas</h3>
        </div>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </section>

      <section class="card history-section">
        <div class="card-title">
          <h3><History :size="20" />Histórico Detalhado</h3>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Ano / Trimestre</th>
                <th>Descrição</th>
                <th class="text-right">Valor (R$)</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="despesa in operatorExpensesData"
                :key="despesa.registro_ans"
              >
                <td>
                  {{ despesa.ano }} / {{ formatTrimester(despesa.trimestre) }}
                </td>
                <td>{{ despesa.descricao }}</td>
                <td
                  class="text-right highlight"
                  :class="moneyColor(despesa.valor_despesas)"
                >
                  {{
                    Number(despesa.valor_despesas).toLocaleString("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    })
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
  gap: 1rem;
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

.details-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
  font-family: "Inter", sans-serif;
  color: #334155;
}

.nav-header {
  margin-bottom: 1.5rem;
}

.btn-back {
  background: transparent;
  border: none;
  color: #64748b;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #2563eb;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 2px 4px -1px rgba(0, 0, 0, 0.03);
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid #f1f5f9;
}

.card-title h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: #0f172a;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.profile-icon {
  background-color: #eff6ff;
  color: #3b82f6;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.company-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  background-color: #f8fafc;
  color: #475569;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #e2e8f0;
}

.tag.uf {
  background-color: #dbeafe;
  color: #1e40af;
  font-weight: 700;
  border-color: #bfdbfe;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.data-table thead th {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8fafc;
  box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.1);
}

.data-table th {
  text-align: left;
  padding: 1rem;
  background-color: #f8fafc;
  color: #64748b;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  border-bottom: 2px solid #e2e8f0;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.data-table tr:hover {
  background-color: #f8fafc;
}

.text-right {
  text-align: right;
}

.highlight {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.text-green {
  color: #16a34a !important;
  font-weight: 700;
}
.text-slate {
  color: #334155;
}

@media (max-width: 768px) {
  .details-page {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .meta-tags {
    justify-content: center;
  }

  .company-name {
    font-size: 1.25rem;
  }

  .chart-container {
    height: 250px;
  }
}
</style>
