# Synchronised Switch group for Home Assistant

Scenario:

A switch is wirted to a ligth bulb, and controls electrically it.
Other switches control the same light bulb, but are not wirted to it.

This normally is done via a set of automations, which detect the change of state for each switch, and syncrhonises the remaining ones.

The problem with this approach is that it is hard to maintain: the more entities are in the group, the more the automations involved.

This integration covers the case above, creating a switch which does the same, but in one single entity configuration.

> Given some switches which needs to be synchronised
> When any of the switches change state
> Then all the other switches change state
> And the group switch also reflect the new state


This is different from a `SwitchGroup` entity, which has only two modes:
- `all` for which the group is on if all the entities are on, otherwise off
- `any` for which the gorup is on if any of the entities are on, otherwise off

To cover the scenario above, it is also needed that any change of state from any entity, will change all the entities and the group state.

## How it works

The group entity determines one master entity, which normally is the one wired to the load to control; and declares all the other entities.

This differentiation is not 100% necessary, but in order to make the update flow simple, the group entity needs to identify a _main_ entity, 
and consider all the other entities `subordinate` to the main one.

This way the group state reflects always the state of the `main`/`master` entity.
When this entity changes state, then the group state is updated, and a change of state action is called on all the other entities.
When any other entity change state, then the `main`/`master` entity is update, triggering the actions above.


## Installation

So far it can be only used via `configuraiton.yaml`

```yaml
switch:
  - platform: synchronised_switch
    name: group
    master_entity: light.master
    entities:
      - light.other_light
      - switch.other_switch
```

The entity_id is computed from the name.