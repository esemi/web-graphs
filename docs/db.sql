CREATE TABLE IF NOT EXISTS `domain` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `domain_full` varchar(255) NOT NULL,
  `date_add` date NOT NULL,
  `last_update_date` datetime DEFAULT NULL,
  `last_update_state` enum('success','error') DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_domains_domain` (`domain_full`),
  KEY `last_update_date` (`last_update_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


CREATE TABLE IF NOT EXISTS `relations` (
  `from_domain_id` int(11) unsigned NOT NULL,
  `to_domain_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`from_domain_id`,`to_domain_id`),
  KEY `to_domain_id` (`to_domain_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE `relations`
  ADD CONSTRAINT `relations_ibfk_4` FOREIGN KEY (`to_domain_id`) REFERENCES `domain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `relations_ibfk_3` FOREIGN KEY (`from_domain_id`) REFERENCES `domain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;