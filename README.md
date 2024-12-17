# Synchronised Switch group for Home Assistant

## Use case

Multiple switches needs to be in the same state. When one changes, the other change as well.

Or in gherkin style:

> Given some switches which needs to be always in the same state
> When any of the switches change state
> Then all the other switches change state

And as a matter of fact, we can also add

> And the group switch also reflect the new state


## Scenario

A switch is wired to a ligth bulb, controlling it electrically.
Other switches control the same light bulb, but are not wired to it.
When any of the switches change state, then all the switches change state.


## How is it done - until now - in Home Assistant?

In home assistant, this normally is done via a set of automations, which detect the change of state for each switch, and syncrhonises the remaining ones.

You need an automation for each switch, triggered by its change of state, turning off any other related automation, change all other switches, and then re-enabling automations back.

This is a complex network of automations, with possible race conditions and not particularely reliable to delays.

The further problem with this approach is that it is hard to maintain: the more entities are in the group, the more the automations involved.
For how much the introductions of categories and labels helped a lot, it's still unpleasant to work with many automations that do the same thing, needs to change together if an amend is needed.

Think of how many groups of automations are needed if you have even just an entire floor with smart switches.


This integration covers the case above, creating a switch which does the same, but in one single entity configuration.

### What about `SwitchGroup`

This integraitons act differently from a `SwitchGroup` entity, which has only two modes:
- `all`: the group is on if all the entities are on, otherwise off
- `any`: the gorup is on if any of the entities are on, otherwise off

To cover the scenario above, it is also needed that any change of state from any entity, will change all the entities and the group state.

## How dows it works?

The group entity determines one entity, which normally is the one wired to the load to control; This entity is internally considered the *master entity*.

The group entity subscribe to state changes for all the entities in the group.

When the master entity switches state, the group:
- change the state of the group entity
- change the state of all the other non-master entities

When a non-master entity switches state, the group:
- change the master entity state (which will trigger the behaviour above)


**Invariant**: The group state reflects always the state of the *master* entity.

**Avoid loops**: since the behaviours above are triggered only on a switch of state, if an entity is already in the needed state, no further action will be done.

## Installation

So far it can be only used via `configuraiton.yaml`

The schema is the same of other `core` group entity schemas.

```yaml
switch:
  - platform: synchronised_switch
    name: group
    entities:
      - light.master
      - light.other_light
      - switch.other_switch
```

The entity_id is computed from the name.