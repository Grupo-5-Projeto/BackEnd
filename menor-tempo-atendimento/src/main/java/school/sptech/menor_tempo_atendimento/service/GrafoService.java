package school.sptech.menor_tempo_atendimento.service;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import school.sptech.menor_tempo_atendimento.Nivel;
import school.sptech.menor_tempo_atendimento.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.domain.Rotas;

import java.util.*;

@Service
public class GrafoService {
    private Map<NoGrafo, List<Par<NoGrafo, Double>>> adjacencia = new HashMap<>();
    @Autowired
    private UpaService upaService;
    private HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa = new HashMap<>();
    private Map<NoGrafo, NoGrafo> predecessores = new HashMap<>();
    private Map<NoGrafo, NoGrafo> rotaMedicos = new HashMap<>();
    private List<NoGrafo> teste = new ArrayList<>();

    private void adicionarNo(NoGrafo no) {
        adjacencia.putIfAbsent(no, new ArrayList<>());
    }

    private void adicionarAresta(NoGrafo origem, NoGrafo destino, double tempoEmMinutos) {
        adjacencia.get(origem).add(new Par<>(destino, tempoEmMinutos));
        adjacencia.get(destino).add(new Par<>(origem, tempoEmMinutos));
    }

    //Metodo para pegar o JSON (API do Maps) e transformar em um HashMap
    //Estou utilizando JsonNode pois achei mais facil de manipular e
    // chegar no resultado final de um NoGrafo
    //Acredito que não é necessário criar classes para cada UPA e Meio de Transporte
    //pois não utilizariamos para mais nada alem de fazer a conversão para NoGrafo
    public HashMap<String, List<Par<String, Integer>>> jsonToHashMap(JsonNode upasProximas) {
        JsonNode upas = upasProximas.get("upas_proximas");
        for (JsonNode upa : upas) {
            String nome = upa.get("nome").asText();
            valorArestaTransporteUpa.putIfAbsent(nome, new ArrayList<>());
            JsonNode modos = upa.get("rotas");
            modos.fields().forEachRemaining(entry -> {
                String transporte = entry.getKey();
                String tempo = entry.getValue().get("Tempo Estimado").asText();

                valorArestaTransporteUpa.get(nome).add(new Par<>(transporte, Integer.parseInt(tempo.replaceAll("[^0-9]", ""))));
            });
        }

        //  Mostrando como fica os valores do hashMap valorArestaTransporteUpa
        for (Map.Entry<String, List<Par<String, Integer>>> entry : valorArestaTransporteUpa.entrySet()) {
            String chave = entry.getKey();
            List<Par<String, Integer>> lista = entry.getValue();

            System.out.println("Chave: " + chave);
            for (Par<String, Integer> par : lista) {
                System.out.println("  -> " + par.chave + " : " + par.valor);
            }
        }

        return valorArestaTransporteUpa;
    }

    //Metodo para os valores do hashMap e adicionar em uma lista de NoGrafo
    //Para depois apenas adicionar os valores do grafo
    public List<NoGrafo> hashMapToNografo() {
        List<NoGrafo> listaAdicionarValoresGrafo = new ArrayList<>();
        int contador = 0;
        for (Map.Entry<String, List<Par<String, Integer>>> entry : valorArestaTransporteUpa.entrySet()) {
            String upa = entry.getKey();
            List<Par<String, Integer>> transporteTempo = entry.getValue();
            listaAdicionarValoresGrafo.add(new NoGrafo(upa, Nivel.NIVEL_UPA, 0));
            //-Criando todos os Nós do meio de transporte
            //-Preciso pegar apenas da primeira vez,
            //pois para os outros valores de upa os meios de transporte se repetem
            if (contador == 0) {
                for (Par<String, Integer> meioDeTransporteDaVez : transporteTempo) {
                    listaAdicionarValoresGrafo.add(new NoGrafo(meioDeTransporteDaVez.chave, Nivel.NIVEL_MEIO_DE_TRANSPORTE, 0));
                }
            }
            contador++;
        }
        return listaAdicionarValoresGrafo;
    }

    //Metodo para gerar o nos de maneira automatica
    //e nao precisar criando na mao
    //Paciente: Padrão -> ponto de inicio, não preciso de nenhuma info
    //MeioDeTransporte: Receber esses valores pela API do Maps
    //Upa: receber valores pela API do Maps (info de tempo do meio de transporte até a UPA)
    //tempo de espera: Receber valores pelo Banco de dados (info fornecida pela Visão computacional que nas UPAs)
    public void gerarNosGrafo(List<NoGrafo> meioDeTransporteUpas) {
        NoGrafo paciente = new NoGrafo("paciente", Nivel.NIVEL_PACIENTE, 0);
        List<String> nomesUpas = new ArrayList<>();
        for (NoGrafo meioDeTransporte : meioDeTransporteUpas) {
            if (meioDeTransporte.getNivel() == Nivel.NIVEL_UPA) {
                nomesUpas.add(meioDeTransporte.getNome());
            }
        }
        List<NoGrafo> temposDeEspera = upaService.getTempoEspera(nomesUpas);
        adicionarNo(paciente);
        for (NoGrafo meiosDeTranporteUpas : meioDeTransporteUpas) adicionarNo(meiosDeTranporteUpas);
        for (NoGrafo tempoDeEspera : temposDeEspera) adicionarNo(tempoDeEspera);
    }

    //Gerar as aresta do grafo de maneira automatica
    //para nao ter que criar na main na mao
    public void gerarArestasGrafo() {
        NoGrafo paciente = null;

        for (NoGrafo no : adjacencia.keySet()) {
            if ("paciente".equals(no.getNome())) {
                paciente = no;
                break;
            }
        }
        for (NoGrafo no : adjacencia.keySet()) {
            if (no.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                adicionarAresta(paciente, no, no.getTempo());
            }
            //- Adicionando arestas entre os meios de transporte e as UPAs
            //- Achar uma UPA
            if (no.getNivel() == Nivel.NIVEL_UPA) {
                //- Procurar por meios de transporte
                for (NoGrafo noDaVez : adjacencia.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                        // Procuro pelo determinado meio de transporte e seu tempo até a determinada upa
                        //OBS: valorArestaTransporteUpa é um HashMap de List<Par<String, Integer>>
                        //Ou seja vou procurar por uma determinada chave (UPA) e irá me retornar
                        //uma lista de pares (meio de transporte, tempo)
                        //Exemplo: UPA 1 -> {Carro, 5}, {Moto, 2}, {Transporte Publico, 10}
                        for (Par<String, Integer> tempoMeioDeTransporteUpa : valorArestaTransporteUpa.get(no.getNome())) {
                            if (tempoMeioDeTransporteUpa.chave.equals(noDaVez.getNome())) {
                                adicionarAresta(no, noDaVez, tempoMeioDeTransporteUpa.valor);
                            }
                        }
                    }
                }
            }
            if (no.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo noDaVez : adjacencia.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                        if (no.getNome().equals(noDaVez.getNome() + "-" + "tempoEspera")) {
                            teste.add(noDaVez);
                            rotaMedicos.put(noDaVez, no);
                            adicionarAresta(no, noDaVez, no.getTempo());
                        }
                    }
                }
            }
        }

    }

    //algoritmo de Dijkstra
    public Map<NoGrafo, Double> algoritmoDijkstra() {
        NoGrafo inicio = null;

        for (NoGrafo no : adjacencia.keySet()) {
            if ("paciente".equals(no.getNome())) {
                inicio = no;
                break;
            }
        }

        Map<NoGrafo, Double> tempoTotal = new HashMap<>();
        PriorityQueue<Par<NoGrafo, Double>> fila = new PriorityQueue<>(Comparator.comparingDouble(p -> p.valor));

        for (NoGrafo no : adjacencia.keySet()) tempoTotal.put(no, Double.MAX_VALUE);
        tempoTotal.put(inicio, 0.0);
        fila.add(new Par<>(inicio, 0.0));

        while (!fila.isEmpty()) {
            Par<NoGrafo, Double> atual = fila.poll();

            for (Par<NoGrafo, Double> vizinho : adjacencia.getOrDefault(atual.chave, Collections.emptyList())) {
                double novoTempo = tempoTotal.get(atual.chave) + vizinho.valor;
                if (novoTempo < tempoTotal.get(vizinho.chave)) {
                    tempoTotal.put(vizinho.chave, novoTempo);
                    predecessores.put(vizinho.chave, atual.chave);
                    fila.add(new Par<>(vizinho.chave, novoTempo));
                }
            }
        }
        System.out.println(tempoTotal);
        return tempoTotal;
    }

    //Metodo para reconstruir o caminho
    //com finalidade de monstrar o melhor caminho para o paciente
    private List<NoGrafo> reconstruirCaminho(NoGrafo destino) {
        List<NoGrafo> caminho = new LinkedList<>();
        NoGrafo atual = destino;
        while (atual != null) {
            caminho.add(0, atual); // insere no início
            atual = predecessores.get(atual);
        }
        return caminho;
    }

    public MelhorCaminho caminhoOtimizado(Map<NoGrafo, Double> tempos) {
        List<NoGrafo> upas = teste;
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
                    .filter(p -> p.chave.equals(medico))
                    .findFirst()
                    .map(p -> p.valor)
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

    //Classe auxiliar para armazenar pares de valores
    private static class Par<K, V> {
        K chave;
        V valor;

        Par(K chave, V valor) {
            this.chave = chave;
            this.valor = valor;
        }
    }

    public void limparDados() {
        adjacencia.clear();
        valorArestaTransporteUpa.clear();
        rotaMedicos.clear();
        predecessores.clear();
        teste.clear();
    }

}
