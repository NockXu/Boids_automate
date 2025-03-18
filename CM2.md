# Automatisation - R4.12

## Plan

1. Principes généraux
2. Outil de modélisation des aspects dynamiques d'un "système"
3. Outil de modélisation de la prise de décision
4. Conclusion

## Rappel

Automates à états finis : modélisation, codage du comportement dynamique d'un "système"

- État encode les modes d'interaction (avec le monde)
- État ne code pas la position dans le monde

## Principes généraux

### Théorie de la déscision

Cadre général (de la réflexion)

1. Module de perception du monde
2. L'entitée à besoin de prendre des déscisions
3. Ses déscisions influence ses actions (et donc ses actions affectent le monde)

4. Objectifs / Scénarios
   influence la déscision

5. Émotions
   Influe sur les déscisions (et inversement)

### La perception

1. la Nature de la perception
    - Discrète : booléenne, label
    - Continue : distance à ?
    - Complexe : simulation de vision

2. Capteurs et déclencheurs (sensors & triggers)

    - Trigger : sortie booléenne
    - Sensor : sortie continue ou discrète (non booléenne)

#### Trigger classique et basique

- Proximité
- Collision

par rapport au monde / par rapport à soi
il est sensible à certain types d'objet

L'automate doit prende des déscision en fonction des données que le trigger lui rapporte

> Attention à la combinatoire

#### Sensor

ex : Vecteur des données des voisins (vitesse, position)