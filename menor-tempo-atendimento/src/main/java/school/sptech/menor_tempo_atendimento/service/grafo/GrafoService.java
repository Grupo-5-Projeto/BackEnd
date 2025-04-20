package school.sptech.menor_tempo_atendimento.service.grafo;

import org.springframework.stereotype.Service;
import school.sptech.menor_tempo_atendimento.util.Nivel;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.domain.Rotas;
import school.sptech.menor_tempo_atendimento.util.Par;

import java.util.*;

@Service
public class GrafoService {
    Map<NoGrafo, List<Par<NoGrafo, Double>>> adjacencia = new HashMap<>();
    private Map<NoGrafo, NoGrafo> predecessores = new HashMap<>();

    public void adicionarNo(NoGrafo no) {
        adjacencia.putIfAbsent(no, new ArrayList<>());
    }

    public void adicionarAresta(NoGrafo origem, NoGrafo destino, double tempoEmMinutos) {
        adjacencia.get(origem).add(new Par<>(destino, tempoEmMinutos));
        adjacencia.get(destino).add(new Par<>(origem, tempoEmMinutos));
    }

    public Map<NoGrafo, Double> algoritmoDijkstra() {
        NoGrafo inicio = null;

        for (NoGrafo no : adjacencia.keySet()) {
            if ("paciente".equals(no.getNome())) {
                inicio = no;
                break;
            }
        }

        Map<NoGrafo, Double> tempoTotal = new HashMap<>();
        PriorityQueue<Par<NoGrafo, Double>> fila = new PriorityQueue<>(Comparator.comparingDouble(p -> p.getValor()));

        for (NoGrafo no : adjacencia.keySet()) tempoTotal.put(no, Double.MAX_VALUE);
        tempoTotal.put(inicio, 0.0);
        fila.add(new Par<>(inicio, 0.0));

        while (!fila.isEmpty()) {
            Par<NoGrafo, Double> atual = fila.poll();

            for (Par<NoGrafo, Double> vizinho : adjacencia.getOrDefault(atual.getChave(), Collections.emptyList())) {
                double novoTempo = tempoTotal.get(atual.getChave()) + vizinho.getValor();
                if (novoTempo < tempoTotal.get(vizinho.getChave())) {
                    tempoTotal.put(vizinho.getChave(), novoTempo);
                    predecessores.put(vizinho.getChave(), atual.getChave());
                    fila.add(new Par<>(vizinho.getChave(), novoTempo));
                }
            }
        }
        System.out.println(tempoTotal);
        return tempoTotal;
    }

    private List<NoGrafo> reconstruirCaminho(NoGrafo destino) {
        List<NoGrafo> caminho = new LinkedList<>();
        NoGrafo atual = destino;
        while (atual != null) {
            caminho.add(0, atual); // insere no início
            atual = predecessores.get(atual);
        }
        return caminho;
    }

    public MelhorCaminho caminhoOtimizado(Map<NoGrafo, Double> tempos, List<NoGrafo> upas, Map<NoGrafo, NoGrafo> rotaMedicos) {
        //this.upas
        double menorTempo = Double.MAX_VALUE;
        List<NoGrafo> melhorRota = new ArrayList<>();

        for (NoGrafo upa : upas) {
            NoGrafo medico = rotaMedicos.get(upa);

            double tempoAteUpa = tempos.getOrDefault(upa, Double.MAX_VALUE);

            // ⚠️ Otimização: se já for pior que o menor tempo encontrado, pula
            if (tempoAteUpa >= menorTempo) {
                System.out.printf("Pulando rota para %s: tempo até UPA (%.2f min) já é pior que atual (%.2f min)%n",
                        upa, tempoAteUpa, menorTempo);
                continue;
            }

            // Tempo da UPA até o médico
            double tempoAteMedico = adjacencia.get(upa).stream()
                    .filter(p -> p.getChave().equals(medico))
                    .findFirst()
                    .map(p -> p.getValor())
                    .orElse(Double.MAX_VALUE);

            List<NoGrafo> caminhoAteUpa = reconstruirCaminho(upa);
            caminhoAteUpa.add(medico); // adiciona o médico no final

            double total = tempoAteUpa + tempoAteMedico;

            if (total < menorTempo) {
                menorTempo = total;
                melhorRota = caminhoAteUpa;
            }

            System.out.printf("Rota: %s | Tempo total: %.2f min%n", caminhoAteUpa, total);
        }

        System.out.println("\nMelhor rota: " + melhorRota);
        System.out.printf("Tempo estimado: %.2f minutos%n", menorTempo);
        MelhorCaminho retorno = new MelhorCaminho();
        Rotas rotas = new Rotas();
        for (NoGrafo no : melhorRota) {
            if (no.getNivel() == Nivel.NIVEL_UPA) retorno.setNome(no.getNome());
            if (no.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) rotas.setModo(no.getNome());
            if (no.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) ;
        }
        rotas.setTempoEstimado(menorTempo);
        retorno.setRotas(rotas);

        return retorno;
    }

    public void limparDados() {
        adjacencia.clear();
        predecessores.clear();
    }

}