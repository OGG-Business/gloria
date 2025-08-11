# Guide de Contribution - Banking Transfer Platform

Merci de votre intérêt pour contribuer au projet Banking Transfer Platform ! Ce document fournit les lignes directrices pour contribuer au projet.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Configuration de l'environnement de développement](#configuration-de-lenvironnement-de-développement)
4. [Standards de code](#standards-de-code)
5. [Tests](#tests)
6. [Documentation](#documentation)
7. [Processus de pull request](#processus-de-pull-request)
8. [Rapport de bugs](#rapport-de-bugs)
9. [Demande de fonctionnalités](#demande-de-fonctionnalités)

## Code de conduite

### Notre engagement

Dans l'intérêt de favoriser un environnement ouvert et accueillant, nous nous engageons, en tant que contributeurs et mainteneurs, à faire de la participation à notre projet et à notre communauté une expérience sans harcèlement pour tous, peu importe l'âge, la taille, le handicap, l'ethnicité, l'identité et l'expression de genre, le niveau d'expérience, la nationalité, l'apparence personnelle, la race, la religion ou l'identité et l'orientation sexuelles.

### Nos standards

Exemples de comportements qui contribuent à créer un environnement positif :

* Utiliser un langage accueillant et inclusif
* Respecter les différents points de vue et expériences
* Accepter gracieusement les critiques constructives
* Se concentrer sur ce qui est le mieux pour la communauté
* Faire preuve d'empathie envers les autres membres de la communauté

Exemples de comportements inacceptables :

* L'utilisation de langage ou d'imagerie sexualisés et d'attention ou d'avances sexuelles non désirées
* Le trolling, les commentaires insultants/désobligeants et les attaques personnelles ou politiques
* Le harcèlement public ou privé
* La publication d'informations privées d'autres personnes, telles que des adresses physiques ou électroniques, sans autorisation explicite
* Toute autre conduite qui pourrait raisonnablement être considérée comme inappropriée dans un cadre professionnel

## Comment contribuer

### Types de contributions

Nous accueillons différents types de contributions :

1. **Rapports de bugs** : Signaler des problèmes ou des comportements inattendus
2. **Demandes de fonctionnalités** : Proposer de nouvelles fonctionnalités
3. **Améliorations de la documentation** : Améliorer la documentation existante
4. **Corrections de bugs** : Corriger des problèmes identifiés
5. **Nouvelles fonctionnalités** : Implémenter de nouvelles fonctionnalités
6. **Améliorations de performance** : Optimiser le code existant
7. **Tests** : Ajouter ou améliorer les tests

### Avant de commencer

1. **Vérifiez les issues existantes** : Recherchez dans les issues existantes pour voir si votre contribution a déjà été discutée
2. **Créez une issue** : Si vous trouvez un bug ou souhaitez proposer une fonctionnalité, créez d'abord une issue
3. **Discutez de votre approche** : Pour les contributions importantes, discutez de votre approche dans l'issue avant de commencer le développement

## Configuration de l'environnement de développement

### Prérequis

- Java 17 ou supérieur
- Node.js 18 ou supérieur
- Docker et Docker Compose
- Git
- IDE recommandé : IntelliJ IDEA ou VS Code

### Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/your-org/banking-transfer-platform.git
   cd banking-transfer-platform
   ```

2. **Configuration de l'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos configurations
   ```

3. **Démarrage des services**
   ```bash
   docker-compose up -d
   ```

4. **Vérification de l'installation**
   ```bash
   # Backend
   curl http://localhost:8080/actuator/health
   
   # Frontend
   curl http://localhost:3000
   ```

### Structure du projet

```
banking-transfer-platform/
├── backend/                 # Application Spring Boot
│   ├── src/main/java/      # Code source Java
│   ├── src/main/resources/ # Ressources (config, migrations)
│   └── src/test/           # Tests
├── frontend/               # Application React
│   ├── src/               # Code source TypeScript
│   ├── public/            # Fichiers publics
│   └── tests/             # Tests
├── infrastructure/         # Configuration infrastructure
├── scripts/               # Scripts utilitaires
├── docs/                  # Documentation
└── data/                  # Données de test
```

## Standards de code

### Java (Backend)

#### Style de code
- Suivre les conventions Java standard
- Utiliser Google Java Style Guide
- Indentation : 4 espaces
- Longueur de ligne maximale : 120 caractères

#### Nommage
- Classes : PascalCase (ex: `TransferService`)
- Méthodes et variables : camelCase (ex: `createTransfer`)
- Constantes : UPPER_SNAKE_CASE (ex: `MAX_TRANSFER_AMOUNT`)
- Packages : lowercase (ex: `com.banking.transfers`)

#### Documentation
```java
/**
 * Service pour la gestion des transferts bancaires.
 * 
 * @author Votre Nom
 * @since 1.0.0
 */
@Service
public class TransferService {
    
    /**
     * Crée un nouveau transfert.
     * 
     * @param request La demande de transfert
     * @return Le transfert créé
     * @throws TransferException si le transfert ne peut pas être créé
     */
    public Transfer createTransfer(TransferRequest request) {
        // Implémentation
    }
}
```

#### Gestion des exceptions
```java
// Utiliser des exceptions spécifiques
public class TransferException extends RuntimeException {
    public TransferException(String message) {
        super(message);
    }
    
    public TransferException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### TypeScript/React (Frontend)

#### Style de code
- Utiliser ESLint et Prettier
- Suivre les conventions React
- Utiliser TypeScript strict mode

#### Nommage
- Composants : PascalCase (ex: `TransferForm`)
- Fonctions et variables : camelCase (ex: `handleSubmit`)
- Constantes : UPPER_SNAKE_CASE (ex: `API_BASE_URL`)
- Fichiers : kebab-case (ex: `transfer-form.tsx`)

#### Documentation
```typescript
/**
 * Composant pour l'affichage d'un formulaire de transfert.
 * 
 * @param props - Les propriétés du composant
 * @returns Le composant de formulaire
 */
interface TransferFormProps {
  /** Callback appelé lors de la soumission */
  onSubmit: (data: TransferData) => void;
  /** Données initiales du formulaire */
  initialData?: Partial<TransferData>;
}

export const TransferForm: React.FC<TransferFormProps> = ({
  onSubmit,
  initialData
}) => {
  // Implémentation
};
```

### SQL (Migrations)

#### Style
- Utiliser des noms de tables en snake_case
- Préfixer les migrations avec V{version}__
- Inclure des commentaires pour les migrations complexes

```sql
-- Migration V2__Add_transfer_events.sql
-- Ajoute la table des événements de transfert pour l'audit

CREATE TABLE transfer_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transfer_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transfer_events_transfer 
        FOREIGN KEY (transfer_id) REFERENCES transfers(id)
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_transfer_events_transfer_id ON transfer_events(transfer_id);
CREATE INDEX idx_transfer_events_type ON transfer_events(event_type);
```

## Tests

### Backend (Java)

#### Tests unitaires
- Utiliser JUnit 5 et Mockito
- Couverture minimale : 70%
- Nommer les tests de manière descriptive

```java
@Test
@DisplayName("Should create transfer when valid data is provided")
void shouldCreateTransferWhenValidDataIsProvided() {
    // Given
    TransferRequest request = createValidTransferRequest();
    
    // When
    Transfer result = transferService.createTransfer(request);
    
    // Then
    assertThat(result).isNotNull();
    assertThat(result.getStatus()).isEqualTo(TransferStatus.INITIATED);
}
```

#### Tests d'intégration
- Utiliser TestContainers pour les tests avec base de données
- Tester les endpoints REST
- Utiliser @SpringBootTest pour les tests complets

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class TransferControllerIntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");
    
    @Test
    void shouldCreateTransferViaApi() {
        // Test d'intégration
    }
}
```

### Frontend (TypeScript)

#### Tests unitaires
- Utiliser Jest et React Testing Library
- Tester les composants et les hooks
- Utiliser des mocks pour les appels API

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { TransferForm } from './TransferForm';

describe('TransferForm', () => {
  it('should submit form with valid data', async () => {
    const mockOnSubmit = jest.fn();
    
    render(<TransferForm onSubmit={mockOnSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/amount/i), {
      target: { value: '100.00' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        amount: '100.00'
      })
    );
  });
});
```

#### Tests E2E
- Utiliser Cypress ou Playwright
- Tester les flux complets
- Inclure des tests de régression

```typescript
// cypress/e2e/transfer.cy.ts
describe('Transfer Flow', () => {
  it('should complete transfer successfully', () => {
    cy.visit('/transfers/new');
    cy.get('[data-testid=amount-input]').type('100.00');
    cy.get('[data-testid=submit-button]').click();
    cy.get('[data-testid=success-message]').should('be.visible');
  });
});
```

## Documentation

### Types de documentation

1. **Documentation technique** : Architecture, API, configuration
2. **Documentation utilisateur** : Guides d'utilisation, tutoriels
3. **Documentation de développement** : Guide de contribution, standards

### Standards de documentation

- Utiliser Markdown
- Inclure des exemples de code
- Maintenir une table des matières
- Mettre à jour régulièrement

### Structure de la documentation

```
docs/
├── INSTALLATION.md          # Guide d'installation
├── API.md                   # Documentation de l'API
├── ARCHITECTURE.md          # Architecture du système
├── SECURITY.md              # Guide de sécurité
├── DEPLOYMENT.md            # Guide de déploiement
├── TROUBLESHOOTING.md       # Guide de dépannage
└── ONBOARDING_SWIFT.md      # Guide d'onboarding SWIFT
```

## Processus de pull request

### 1. Préparation

- Créer une branche à partir de `main`
- Nommer la branche : `feature/description` ou `fix/description`
- S'assurer que les tests passent localement

### 2. Développement

- Suivre les standards de code
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation si nécessaire
- Commiter régulièrement avec des messages descriptifs

### 3. Soumission

- Créer une pull request
- Remplir le template de PR
- Ajouter des reviewers appropriés
- Lier les issues concernées

### Template de Pull Request

```markdown
## Description
Brève description des changements apportés.

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Amélioration de performance
- [ ] Documentation
- [ ] Refactoring

## Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration ajoutés/mis à jour
- [ ] Tests E2E ajoutés/mis à jour
- [ ] Tous les tests passent

## Documentation
- [ ] Documentation mise à jour
- [ ] Aucune documentation nécessaire

## Checklist
- [ ] Code conforme aux standards
- [ ] Tests ajoutés et passants
- [ ] Documentation mise à jour
- [ ] Aucun secret exposé
- [ ] Variables d'environnement documentées

## Screenshots (si applicable)
Ajouter des captures d'écran pour les changements UI.

## Informations supplémentaires
Toute information supplémentaire pertinente.
```

### 4. Review

- Répondre aux commentaires des reviewers
- Faire les modifications demandées
- S'assurer que tous les checks passent

### 5. Merge

- Squash et merge en `main`
- Supprimer la branche après merge

## Rapport de bugs

### Template de rapport de bug

```markdown
## Description du bug
Description claire et concise du bug.

## Étapes pour reproduire
1. Aller à '...'
2. Cliquer sur '...'
3. Faire défiler jusqu'à '...'
4. Voir l'erreur

## Comportement attendu
Description claire de ce qui devrait se passer.

## Comportement actuel
Description de ce qui se passe actuellement.

## Captures d'écran
Si applicable, ajouter des captures d'écran.

## Environnement
- OS: [ex: Windows 10, macOS 12.0]
- Navigateur: [ex: Chrome 96, Safari 15]
- Version: [ex: 1.2.0]

## Informations supplémentaires
Toute autre information pertinente.
```

## Demande de fonctionnalités

### Template de demande de fonctionnalité

```markdown
## Problème
Description claire du problème que cette fonctionnalité résoudrait.

## Solution proposée
Description claire de la solution souhaitée.

## Alternatives considérées
Description des alternatives considérées.

## Informations supplémentaires
Toute autre information pertinente.
```

## Contact

Pour toute question concernant la contribution :

- **Issues GitHub** : [Créer une issue](https://github.com/your-org/banking-transfer-platform/issues)
- **Email** : contribute@banking-transfer-platform.com
- **Discord** : [Rejoindre le serveur](https://discord.gg/banking-transfer)

## Remerciements

Merci à tous les contributeurs qui participent à l'amélioration de ce projet !

---

**Note** : Ce guide est un document vivant qui évolue avec le projet. N'hésitez pas à proposer des améliorations via une pull request.