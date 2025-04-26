package school.sptech.menor_tempo_atendimento.domain;

import school.sptech.menor_tempo_atendimento.domain.Rotas;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.domain.Nivel;
import school.sptech.menor_tempo_atendimento.domain.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Par;

import java.util.*;

public class Dijkstra {

    private Map<NoGrafo, NoGrafo> predecessores;

    public Dijkstra() {
        this.predecessores = new HashMap<>();
    }

    public Map<NoGrafo, Double> algoritmoDijkstra(Map<NoGrafo, List<Par<NoGrafo, Double>>> adjacencia) {
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

    public MelhorCaminho caminhoOtimizado(Map<NoGrafo, Double> tempos, Map<NoGrafo, List<Par<NoGrafo, Double>>> adjacencia) {
        double menorTempo = Double.MAX_VALUE;
        List<NoGrafo> melhorRota = new ArrayList<>();
        Map<NoGrafo, NoGrafo> mapUpaAtendimento = getMapUpaAtendimento(adjacencia);
        for (NoGrafo upa : getListUpa(adjacencia)) {
            NoGrafo upaAtendimento = mapUpaAtendimento.get(upa);

            double tempoAteUpa = tempos.getOrDefault(upa, Double.MAX_VALUE);

            double tempoAtendimento = adjacencia.get(upa).stream()
                    .filter(p -> p.getChave().equals(upaAtendimento))
                    .findFirst()
                    .map(p -> p.getValor())
                    .orElse(Double.MAX_VALUE);

            List<NoGrafo> caminhoAteUpa = reconstruirCaminho(upa);
            caminhoAteUpa.add(upaAtendimento); // adiciona o upaAtendimento no final

            double total = tempoAteUpa + tempoAtendimento;

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
        }
        rotas.setTempoEstimado(menorTempo);
        retorno.setRotas(rotas);

        return retorno;
    }

    private Map<NoGrafo, NoGrafo> getMapUpaAtendimento(Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo){
        Map<NoGrafo, NoGrafo> rotaMedicos = new HashMap<>();
        for (NoGrafo noDaVez : grafo.keySet()) {
            if (noDaVez.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo vizinho : grafo.keySet()) {
                    if (vizinho.getNivel() == Nivel.NIVEL_UPA) {
                        if (noDaVez.getNome().equals(vizinho.getNome() + "-" + "tempoEspera")) {
                            rotaMedicos.put(vizinho, noDaVez);
                        }
                    }
                }

            }
        }
        return rotaMedicos;
    }

    private List<NoGrafo> getListUpa(Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo){
        List<NoGrafo> listaUpas = new ArrayList<>();
        for (NoGrafo noDaVez : grafo.keySet()) {
            if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                listaUpas.add(noDaVez);
            }
        }
        return listaUpas;
    }

}
